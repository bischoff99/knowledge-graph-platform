"""
ETL Engine - Config-driven data ingestion to Neo4j
Supports idempotent upserts, batch processing, M3 Max parallelization
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from neo4j import GraphDatabase
import pandas as pd

from config_schema import ETLJobConfig, PropertyMapping, EntityMapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLEngine:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.executor = None
    
    def close(self):
        self.driver.close()
        if self.executor:
            self.executor.shutdown(wait=True)
    
    def transform_value(self, value: Any, transform: Optional[str]) -> Any:
        """Apply transformation to field value"""
        if transform is None:
            return value
        
        transforms = {
            'lowercase': lambda v: str(v).lower() if v else None,
            'uppercase': lambda v: str(v).upper() if v else None,
            'timestamp': lambda v: datetime.fromisoformat(str(v)) if v else None,
            'json_parse': lambda v: eval(v) if isinstance(v, str) else v,
            'str': lambda v: str(v) if v is not None else None
        }
        
        return transforms.get(transform, lambda v: v)(value)
    
    def build_entity_cypher(self, mapping: EntityMapping, records: List[Dict]) -> tuple[str, Dict]:
        """Build MERGE cypher for batch entity upsert"""
        # Build property assignment
        props = []
        for pm in mapping.properties:
            props.append(f"n.{pm.target_property} = row.{pm.target_property}")
        
        # Add metadata
        if mapping.meta_fields:
            for key, value in mapping.meta_fields.items():
                if value == "now()":
                    props.append(f"n.{key} = datetime()")
                else:
                    props.append(f"n.{key} = '{value}'")
        
        # Build tags
        if mapping.tags_field:
            props.append(f"n.tags = split(row.{mapping.tags_field}, ',')")
        
        cypher = f"""
        UNWIND $batch AS row
        MERGE (n:{mapping.label} {{id: row.{mapping.id_field}}})
        ON CREATE SET {', '.join(props)}, n.created_at = datetime()
        ON MATCH SET {', '.join(props)}, n.updated_at = datetime()
        """
        
        # Transform records
        batch_data = []
        for record in records:
            transformed = {}
            for pm in mapping.properties:
                source_val = record.get(pm.source_field, pm.default)
                transformed[pm.target_property] = self.transform_value(source_val, pm.transform)
            
            if mapping.tags_field and mapping.tags_field in record:
                transformed[mapping.tags_field] = record[mapping.tags_field]
            
            batch_data.append(transformed)
        
        return cypher, {"batch": batch_data}
    
    def execute_batch(self, cypher: str, params: Dict) -> int:
        """Execute batch write to Neo4j"""
        with self.driver.session() as session:
            result = session.run(cypher, params)
            summary = result.consume()
            return summary.counters.nodes_created + summary.counters.nodes_merged
    
    async def run_job(self, config: ETLJobConfig) -> Dict[str, Any]:
        """Execute complete ETL job"""
        logger.info(f"Starting ETL job: {config.name}")
        start_time = datetime.now()
        
        # Load data from source
        if config.source.type == 'csv':
            df = pd.read_csv(config.source.connection['path'])
        elif config.source.type == 'json':
            df = pd.read_json(config.source.connection['path'])
        elif config.source.type == 'postgres':
            # Requires SQLAlchemy engine
            pass
        else:
            raise ValueError(f"Unsupported source type: {config.source.type}")
        
        records = df.to_dict('records')
        logger.info(f"Loaded {len(records)} records from {config.source.type}")
        
        # Process entity mappings in batches
        total_nodes = 0
        for mapping in config.entity_mappings:
            logger.info(f"Processing entity mapping: {mapping.label}")
            
            # Split into batches
            batches = [records[i:i+config.batch_size] for i in range(0, len(records), config.batch_size)]
            
            # M3 Max parallel processing
            self.executor = ThreadPoolExecutor(max_workers=min(32, config.parallel_workers))
            
            for i, batch in enumerate(batches):
                cypher, params = self.build_entity_cypher(mapping, batch)
                nodes_processed = self.executor.submit(self.execute_batch, cypher, params).result()
                total_nodes += nodes_processed
                logger.info(f"Batch {i+1}/{len(batches)}: {nodes_processed} nodes")
            
            self.executor.shutdown(wait=True)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": "success",
            "job": config.name,
            "records_processed": len(records),
            "nodes_created": total_nodes,
            "duration_seconds": duration,
            "throughput": len(records) / duration if duration > 0 else 0
        }


if __name__ == '__main__':
    # Example usage
    engine = ETLEngine(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test1234"
    )
    
    # Load config and run
    # result = asyncio.run(engine.run_job(EXAMPLE_CONFIG))
    # print(result)
    
    engine.close()
