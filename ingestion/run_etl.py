#!/usr/bin/env python3
"""
ETL CLI Runner
Execute ETL jobs from YAML configuration files
"""

import asyncio
import sys
import yaml
from pathlib import Path

from config_schema import ETLJobConfig
from etl_engine import ETLEngine


def load_config(config_path: str) -> ETLJobConfig:
    """Load ETL job configuration from YAML"""
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)
    return ETLJobConfig(**config_dict)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python run_etl.py <config.yaml>")
        print("Example: python run_etl.py example_job.yaml")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    # Load configuration
    print(f"Loading ETL config: {config_path}")
    config = load_config(config_path)
    
    # Initialize engine
    engine = ETLEngine(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test1234"
    )
    
    try:
        # Run job
        result = await engine.run_job(config)
        
        # Print results
        print("\n" + "=" * 70)
        print("ETL JOB COMPLETE")
        print("=" * 70)
        print(f"Job: {result['job']}")
        print(f"Records processed: {result['records_processed']}")
        print(f"Nodes created: {result['nodes_created']}")
        print(f"Duration: {result['duration_seconds']:.2f}s")
        print(f"Throughput: {result['throughput']:.1f} records/sec")
        print("=" * 70)
        
    finally:
        engine.close()


if __name__ == '__main__':
    asyncio.run(main())
