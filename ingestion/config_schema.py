"""
ETL Configuration Schema
Defines mapping from data sources to Neo4j entities
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class PropertyMapping(BaseModel):
    """Maps source field to graph property"""
    source_field: str
    target_property: str
    transform: Optional[str] = None  # 'lowercase', 'uppercase', 'timestamp', 'json_parse'
    default: Optional[Any] = None


class EntityMapping(BaseModel):
    """Maps source record to Neo4j node"""
    label: str  # Neo4j label (e.g., 'Project', 'Tool')
    id_field: str  # Unique identifier field
    properties: List[PropertyMapping]
    tags_field: Optional[str] = None  # Comma-separated tags
    meta_fields: Optional[Dict[str, str]] = Field(default_factory=dict)  # Auto-added metadata


class RelationshipMapping(BaseModel):
    """Maps source data to Neo4j relationship"""
    type: str  # Relationship type (e.g., 'DEPENDS_ON')
    from_field: str  # Source entity ID field
    to_field: str  # Target entity ID field
    properties: List[PropertyMapping] = Field(default_factory=list)


class SourceConfig(BaseModel):
    """Data source configuration"""
    type: str  # 'csv', 'json', 'postgres', 'api'
    connection: Dict[str, Any]  # Connection params
    query: Optional[str] = None  # SQL query or API endpoint


class ETLJobConfig(BaseModel):
    """Complete ETL job configuration"""
    name: str
    description: str
    source: SourceConfig
    entity_mappings: List[EntityMapping]
    relationship_mappings: List[RelationshipMapping] = Field(default_factory=list)
    batch_size: int = 1000
    parallel_workers: int = 16  # M3 Max optimization
    upsert_strategy: str = 'MERGE'  # 'MERGE' or 'CREATE'


# Example configuration (can be loaded from YAML/JSON)
EXAMPLE_CONFIG = ETLJobConfig(
    name="easypost_shipments",
    description="Import EasyPost shipments as Project entities",
    source=SourceConfig(
        type="postgres",
        connection={
            "host": "localhost",
            "database": "easypost",
            "user": "postgres",
            "password": "password"
        },
        query="SELECT id, tracking_code, status, created_at FROM shipments WHERE status = 'delivered'"
    ),
    entity_mappings=[
        EntityMapping(
            label="Shipment",
            id_field="id",
            properties=[
                PropertyMapping(source_field="id", target_property="shipment_id"),
                PropertyMapping(source_field="tracking_code", target_property="tracking_number"),
                PropertyMapping(source_field="status", target_property="status"),
                PropertyMapping(source_field="created_at", target_property="created_at", transform="timestamp")
            ],
            meta_fields={"source": "easypost", "import_date": "now()"}
        )
    ],
    batch_size=5000,
    parallel_workers=32
)
