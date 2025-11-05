"""
GraphRAG Subgraph Retrieval
Intelligent context retrieval for LLM augmentation
"""

import logging
from typing import List, Dict, Any, Optional, Set
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphRAGRetriever:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def close(self):
        self.driver.close()
    
    def k_hop_subgraph(self, seed_entities: List[str], k: int = 2, 
                       max_nodes: int = 50) -> Dict[str, Any]:
        """
        Retrieve k-hop neighborhood around seed entities
        
        Args:
            seed_entities: Entity IDs or names to start from
            k: Number of hops (1-3 recommended)
            max_nodes: Limit subgraph size for context window
        
        Returns:
            Subgraph with nodes, edges, and metadata
        """
        cypher = """
        // Find seed nodes
        UNWIND $seeds AS seed
        MATCH (n)
        WHERE n.id = seed OR n.name = seed
        
        // Get k-hop neighborhood
        CALL apoc.path.subgraphAll(n, {
            maxLevel: $k,
            limit: $max_nodes
        })
        YIELD nodes, relationships
        
        RETURN nodes, relationships
        """
        
        with self.driver.session() as session:
            result = session.run(cypher, seeds=seed_entities, k=k, max_nodes=max_nodes)
            record = result.single()
            
            if not record:
                return {"nodes": [], "relationships": [], "count": 0}
            
            nodes = [dict(node) for node in record["nodes"]]
            rels = [
                {
                    "from": dict(rel.start_node)["name"],
                    "to": dict(rel.end_node)["name"],
                    "type": rel.type,
                    "properties": dict(rel)
                }
                for rel in record["relationships"]
            ]
            
            return {
                "nodes": nodes,
                "relationships": rels,
                "count": len(nodes),
                "hops": k,
                "seeds": seed_entities
            }
    
    def semantic_subgraph(self, query: str, top_k: int = 10, 
                          expand_hops: int = 1) -> Dict[str, Any]:
        """
        Semantic search followed by neighborhood expansion
        
        Args:
            query: Natural language query
            top_k: Number of initial matches
            expand_hops: Hops to expand around matches
        
        Returns:
            Relevant subgraph for RAG context
        """
        # Full-text search for seed nodes
        search_cypher = """
        CALL db.index.fulltext.queryNodes('faq_content', $query)
        YIELD node, score
        RETURN node, score
        LIMIT $top_k
        """
        
        with self.driver.session() as session:
            search_result = session.run(search_cypher, query=query, top_k=top_k)
            seed_nodes = [record["node"]["name"] for record in search_result]
            
            if not seed_nodes:
                # Fallback to CONTAINS search
                fallback_result = session.run("""
                    MATCH (n)
                    WHERE n.name CONTAINS $query 
                       OR any(tag IN n.tags WHERE tag CONTAINS $query)
                    RETURN n.name AS name
                    LIMIT $top_k
                """, query=query, top_k=top_k)
                seed_nodes = [record["name"] for record in fallback_result]
        
        if not seed_nodes:
            logger.warning(f"No entities found for query: {query}")
            return {"nodes": [], "relationships": [], "query": query}
        
        # Expand neighborhood
        logger.info(f"Found {len(seed_nodes)} seed nodes, expanding {expand_hops} hops")
        subgraph = self.k_hop_subgraph(seed_nodes, k=expand_hops, max_nodes=50)
        subgraph["query"] = query
        subgraph["method"] = "semantic_search + k_hop_expansion"
        
        return subgraph
    
    def path_based_retrieval(self, entity_a: str, entity_b: str, 
                            max_paths: int = 5) -> Dict[str, Any]:
        """
        Find paths between two entities (for explaining relationships)
        
        Args:
            entity_a: Start entity ID or name
            entity_b: End entity ID or name
            max_paths: Maximum paths to return
        
        Returns:
            Paths with nodes and relationships
        """
        cypher = """
        MATCH (a), (b)
        WHERE (a.id = $entity_a OR a.name = $entity_a)
          AND (b.id = $entity_b OR b.name = $entity_b)
        
        MATCH path = allShortestPaths((a)-[*..6]-(b))
        RETURN path
        LIMIT $max_paths
        """
        
        with self.driver.session() as session:
            result = session.run(cypher, entity_a=entity_a, entity_b=entity_b, max_paths=max_paths)
            
            paths = []
            for record in result:
                path = record["path"]
                paths.append({
                    "length": len(path.relationships),
                    "nodes": [node["name"] for node in path.nodes],
                    "relationships": [rel.type for rel in path.relationships]
                })
            
            return {
                "from": entity_a,
                "to": entity_b,
                "paths": paths,
                "count": len(paths)
            }
    
    def community_subgraph(self, community_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        Retrieve community/cluster subgraph
        Useful for topic-specific context retrieval
        """
        # Requires community detection algorithm (Louvain, Label Propagation)
        # Run as preprocessing: CALL gds.louvain.write(...)
        
        cypher = """
        MATCH (n)
        WHERE n.community = $community_id
        
        CALL apoc.path.subgraphAll(n, {maxLevel: $depth})
        YIELD nodes, relationships
        
        RETURN nodes, relationships
        """
        
        with self.driver.session() as session:
            result = session.run(cypher, community_id=community_id, depth=depth)
            record = result.single()
            
            if not record:
                return {"nodes": [], "relationships": []}
            
            return {
                "nodes": [dict(node) for node in record["nodes"]],
                "relationships": [
                    {"from": dict(rel.start_node)["name"], "to": dict(rel.end_node)["name"], "type": rel.type}
                    for rel in record["relationships"]
                ]
            }


if __name__ == '__main__':
    # Example usage
    retriever = GraphRAGRetriever(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test1234"
    )
    
    # Semantic retrieval
    subgraph = retriever.semantic_subgraph("optimize M3 Max performance", top_k=5, expand_hops=2)
    print(f"Retrieved subgraph: {subgraph['count']} nodes for RAG context")
    
    # Path-based retrieval
    paths = retriever.path_based_retrieval("EasyPost MCP Project", "Desktop Commander MCP")
    print(f"Found {paths['count']} paths between entities")
    
    retriever.close()
