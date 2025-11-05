#!/usr/bin/env python3
"""
Database Migration Runner
Applies pending Cypher migrations to Neo4j
"""

import hashlib
from pathlib import Path
from neo4j import GraphDatabase


def get_migration_checksum(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def get_applied_migrations(driver):
    """Get list of applied migration versions"""
    with driver.session() as session:
        result = session.run("""
            MATCH (m:Migration)
            RETURN m.version AS version
            ORDER BY m.version
        """)
        return [record["version"] for record in result]


def apply_migration(driver, version: str, name: str, content: str):
    """Apply a single migration"""
    checksum = get_migration_checksum(content)
    
    with driver.session() as session:
        # Execute migration
        for statement in content.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('//'):
                session.run(statement)
        
        # Track migration
        session.run("""
            CREATE (m:Migration {
                version: $version,
                name: $name,
                applied_at: datetime(),
                checksum: $checksum
            })
        """, version=version, name=name, checksum=checksum)
    
    print(f"✅ Applied migration {version}: {name}")


def main():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "test1234"))
    
    # Get applied migrations
    applied = set(get_applied_migrations(driver))
    
    # Get pending migrations
    migrations_dir = Path("ops/migrations")
    migration_files = sorted(migrations_dir.glob("*.cypher"))
    
    pending = []
    for migration_file in migration_files:
        version = migration_file.stem.split('_')[0]
        if version not in applied:
            pending.append(migration_file)
    
    if not pending:
        print("✅ No pending migrations")
        driver.close()
        return
    
    print(f"📋 Found {len(pending)} pending migrations")
    
    for migration_file in pending:
        parts = migration_file.stem.split('_', 1)
        version = parts[0]
        name = parts[1] if len(parts) > 1 else "unknown"
        
        content = migration_file.read_text()
        apply_migration(driver, version, name, content)
    
    driver.close()
    print(f"\n✅ Applied {len(pending)} migrations")


if __name__ == '__main__':
    main()
