#!/usr/bin/env python3
"""
Schema Validation Tests
Ensures graph structure integrity and data quality
"""

import pytest
from neo4j import GraphDatabase


class TestGraphSchema:
    @pytest.fixture(scope="class")
    def driver(self):
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "test1234")
        )
        yield driver
        driver.close()
    
    def test_constraints_exist(self, driver):
        """Verify all required constraints are created"""
        with driver.session() as session:
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]
            
            required = ["project_name", "project_id", "config_name", "tool_name", "pattern_name", "doc_name"]
            missing = [c for c in required if c not in constraints]
            
            assert not missing, f"Missing constraints: {missing}"
    
    def test_indexes_exist(self, driver):
        """Verify all required indexes are created"""
        with driver.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]
            
            required = ["project_status", "tool_status", "entity_tags"]
            missing = [idx for idx in required if idx not in indexes]
            
            assert not missing, f"Missing indexes: {missing}"
    
    def test_no_orphaned_nodes(self, driver):
        """Check for nodes with no relationships"""
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE NOT (n)--()
                RETURN count(n) AS orphans
            """)
            orphans = result.single()["orphans"]
            
            # Allow some orphans (e.g., root entities), but flag excessive
            assert orphans < 5, f"Too many orphaned nodes: {orphans}"
    
    def test_no_duplicate_entities(self, driver):
        """Check for duplicate entity names"""
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                WITH n.name AS name, count(*) AS count
                WHERE count > 1 AND name IS NOT NULL
                RETURN name, count
            """)
            
            duplicates = [(record["name"], record["count"]) for record in result]
            assert not duplicates, f"Duplicate entities found: {duplicates}"
    
    def test_temporal_fields_present(self, driver):
        """Verify temporal tracking on critical entities"""
        with driver.session() as session:
            result = session.run("""
                MATCH (n:Project)
                WHERE n.last_verified IS NULL OR n.created_at IS NULL
                RETURN n.name AS name
            """)
            
            missing = [record["name"] for record in result]
            assert not missing, f"Projects missing temporal fields: {missing}"
    
    def test_criticality_levels_valid(self, driver):
        """Ensure criticality values are from allowed set"""
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.criticality IS NOT NULL
                  AND NOT n.criticality IN ['critical', 'high', 'medium', 'low']
                RETURN n.name AS name, n.criticality AS level
            """)
            
            invalid = [(record["name"], record["level"]) for record in result]
            assert not invalid, f"Invalid criticality levels: {invalid}"
    
    def test_tags_are_lists(self, driver):
        """Verify tags property is always a list"""
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.tags IS NOT NULL AND NOT n.tags IS :: LIST
                RETURN n.name AS name
            """)
            
            invalid = [record["name"] for record in result]
            assert not invalid, f"Entities with non-list tags: {invalid}"


if __name__ == '__main__':
    pytest.main([__file__, "-v"])
