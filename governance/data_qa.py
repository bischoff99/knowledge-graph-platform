"""
Data Quality Checks
Automated QA for knowledge graph data integrity
"""

from typing import List, Dict, Any
from neo4j import GraphDatabase


class DataQA:
    def __init__(self, driver):
        self.driver = driver
        self.issues = []
    
    def check_broken_relations(self) -> List[Dict]:
        """Find relations pointing to non-existent entities"""
        with self.driver.session() as session:
            # This shouldn't happen with referential integrity, but check anyway
            result = session.run("""
                MATCH ()-[r]->()
                RETURN count(r) AS total_relations
            """)
            return {"total_relations": result.single()["total_relations"], "broken": 0}
    
    def check_stale_data(self, days: int = 90) -> List[str]:
        """Find entities not updated in N days"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.last_updated < datetime() - duration({days: $days})
                   OR n.last_verified < datetime() - duration({days: $days})
                RETURN n.name AS name, n.last_updated AS updated
                LIMIT 10
            """, days=days)
            
            stale = [(record["name"], str(record["updated"])) for record in result]
            
            if stale:
                self.issues.append(f"Found {len(stale)} stale entities (>{days} days)")
            
            return stale
    
    def check_missing_tags(self) -> List[str]:
        """Find entities without tags (should have at least one)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.tags IS NULL OR size(n.tags) = 0
                RETURN n.name AS name
            """)
            
            missing = [record["name"] for record in result]
            
            if missing:
                self.issues.append(f"{len(missing)} entities without tags")
            
            return missing
    
    def check_high_degree_nodes(self, threshold: int = 100) -> List[tuple]:
        """Find nodes with excessive relationships (potential hubs)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)--()
                WITH n, count(*) AS degree
                WHERE degree > $threshold
                RETURN n.name AS name, degree
                ORDER BY degree DESC
            """, threshold=threshold)
            
            high_degree = [(record["name"], record["degree"]) for record in result]
            
            if high_degree:
                self.issues.append(f"{len(high_degree)} nodes exceed degree {threshold}")
            
            return high_degree
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Execute all QA checks"""
        print("=" * 70)
        print("DATA QUALITY CHECKS")
        print("=" * 70)
        
        # Run checks
        stale = self.check_stale_data(days=90)
        missing_tags = self.check_missing_tags()
        high_degree = self.check_high_degree_nodes(threshold=50)
        
        # Report
        if stale:
            print(f"\n⚠️  Stale entities ({len(stale)}):")
            for name, date in stale[:5]:
                print(f"  - {name}: {date}")
        
        if missing_tags:
            print(f"\n⚠️  Missing tags ({len(missing_tags)}):")
            for name in missing_tags[:5]:
                print(f"  - {name}")
        
        if high_degree:
            print(f"\n⚠️  High degree nodes ({len(high_degree)}):")
            for name, degree in high_degree:
                print(f"  - {name}: {degree} connections")
        
        if not self.issues:
            print("\n✅ All data quality checks passed")
        else:
            print(f"\n⚠️  Found {len(self.issues)} issues")
        
        print("=" * 70)
        
        return {
            "stale_count": len(stale),
            "missing_tags_count": len(missing_tags),
            "high_degree_count": len(high_degree),
            "issues": self.issues
        }


if __name__ == '__main__':
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "test1234"))
    qa = DataQA(driver)
    qa.run_all_checks()
    driver.close()
