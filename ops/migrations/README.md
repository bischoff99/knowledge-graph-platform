# Database Migrations

Cypher-based migrations for schema evolution.

## Convention

- Filename: `NNN_description.cypher` (e.g., `001_initial_schema.cypher`)
- Each migration is idempotent (use `IF NOT EXISTS`)
- Track applied migrations in `:Migration` nodes

## Applying Migrations

### Manually
```bash
cat ops/migrations/001_initial_schema.cypher | cypher-shell -u neo4j -p password
```

### Via Migration Tool
```bash
python ops/run_migrations.py
```

## Creating Migrations

```bash
# Create new migration
./ops/create_migration.sh "add_user_entities"
# Creates: ops/migrations/002_add_user_entities.cypher

# Edit migration file
# Add idempotent Cypher statements

# Apply
python ops/run_migrations.py
```

## Migration Tracking

Migrations are tracked in the graph:
```cypher
CREATE (m:Migration {
  version: '001',
  name: 'initial_schema',
  applied_at: datetime(),
  checksum: 'sha256-hash'
})
```

Query migration history:
```cypher
MATCH (m:Migration)
RETURN m.version, m.name, m.applied_at
ORDER BY m.version
```
