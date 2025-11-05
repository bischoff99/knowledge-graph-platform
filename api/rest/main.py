"""
Knowledge Graph REST API
FastAPI service for common graph queries and operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase
import os

app = FastAPI(
    title="Knowledge Graph API",
    description="REST API for querying and updating the knowledge graph",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j connection
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "test1234"))
)


# Models
class EntityResponse(BaseModel):
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    tags: List[str]


class RelationshipResponse(BaseModel):
    from_entity: str
    to_entity: str
    type: str
    properties: Dict[str, Any]


class GraphStatsResponse(BaseModel):
    total_entities: int
    total_relationships: int
    entity_types: Dict[str, int]
    relationship_types: Dict[str, int]


# Endpoints
@app.get("/")
async def root():
    return {
        "service": "Knowledge Graph REST API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "search": "/search?q=query",
            "entity": "/entities/{entity_id}",
            "patterns": "/patterns",
            "dependencies": "/dependencies/{project_id}"
        }
    }


@app.get("/health")
async def health():
    """Health check with Neo4j connection status"""
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS health")
            result.single()
        return {"status": "healthy", "neo4j": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Neo4j unavailable: {str(e)}")


@app.get("/stats", response_model=GraphStatsResponse)
async def get_stats():
    """Get knowledge graph statistics"""
    with driver.session() as session:
        # Count entities by type
        entity_result = session.run("""
            MATCH (n)
            RETURN labels(n) AS type, count(*) AS count
        """)
        entity_types = {
            ",".join(record["type"]): record["count"] 
            for record in entity_result
        }
        
        # Count relationships by type
        rel_result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(*) AS count
        """)
        relationship_types = {
            record["type"]: record["count"]
            for record in rel_result
        }
        
        # Totals
        total_entities = sum(entity_types.values())
        total_relationships = sum(relationship_types.values())
        
        return GraphStatsResponse(
            total_entities=total_entities,
            total_relationships=total_relationships,
            entity_types=entity_types,
            relationship_types=relationship_types
        )


@app.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, le=100, description="Max results")
):
    """Full-text search across entities"""
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            WHERE n.name CONTAINS $query 
               OR any(tag IN n.tags WHERE tag CONTAINS $query)
               OR n.description CONTAINS $query
            RETURN n
            LIMIT $limit
        """, query=q, limit=limit)
        
        entities = []
        for record in result:
            node = record["n"]
            entities.append({
                "id": node.get("id"),
                "name": node.get("name"),
                "type": list(node.labels)[0] if node.labels else "Unknown",
                "tags": node.get("tags", []),
                "description": node.get("description")
            })
        
        return {"query": q, "results": entities, "count": len(entities)}


@app.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get entity by ID with relationships"""
    with driver.session() as session:
        # Get entity
        entity_result = session.run("""
            MATCH (n {id: $entity_id})
            RETURN n, labels(n) AS labels
        """, entity_id=entity_id)
        
        record = entity_result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        node = record["n"]
        labels = record["labels"]
        
        # Get relationships
        rel_result = session.run("""
            MATCH (n {id: $entity_id})-[r]-(m)
            RETURN type(r) AS type, m.name AS related_entity, 
                   startNode(r).id = $entity_id AS is_outgoing
        """, entity_id=entity_id)
        
        relationships = [
            {
                "type": r["type"],
                "entity": r["related_entity"],
                "direction": "out" if r["is_outgoing"] else "in"
            }
            for r in rel_result
        ]
        
        return {
            "id": node.get("id"),
            "name": node.get("name"),
            "labels": labels,
            "properties": dict(node),
            "relationships": relationships
        }


@app.get("/patterns")
async def get_patterns():
    """Get all design patterns with implementations"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Pattern)
            OPTIONAL MATCH (proj:Project)-[:IMPLEMENTS_PATTERN]->(p)
            RETURN p, collect(proj.name) AS implementations
        """)
        
        patterns = []
        for record in result:
            pattern = record["p"]
            patterns.append({
                "id": pattern.get("id"),
                "name": pattern.get("name"),
                "formula": pattern.get("formula"),
                "proven_speedup": pattern.get("proven_speedup"),
                "implementations": record["implementations"]
            })
        
        return {"patterns": patterns, "count": len(patterns)}


@app.get("/dependencies/{project_id}")
async def get_dependencies(
    project_id: str,
    depth: int = Query(3, le=10, description="Dependency depth")
):
    """Get project dependencies up to specified depth"""
    with driver.session() as session:
        result = session.run("""
            MATCH path = (p:Project {id: $project_id})-[:DEPENDS_ON_CRITICAL*1..$depth]->()
            RETURN path
        """, project_id=project_id, depth=depth)
        
        dependencies = []
        seen = set()
        
        for record in result:
            path = record["path"]
            for node in path.nodes:
                if node.get("id") not in seen:
                    seen.add(node.get("id"))
                    dependencies.append({
                        "id": node.get("id"),
                        "name": node.get("name"),
                        "criticality": node.get("criticality")
                    })
        
        return {
            "project_id": project_id,
            "depth": depth,
            "dependencies": dependencies,
            "count": len(dependencies)
        }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
