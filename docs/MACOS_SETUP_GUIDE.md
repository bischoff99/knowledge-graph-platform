# macOS Setup Guide - Knowledge Graph Platform

Complete setup instructions for macOS development environment.

## Prerequisites

### 1. Install Docker Desktop
```bash
# If not already installed
brew install --cask docker

# Start Docker Desktop
open -a Docker

# Verify (wait 30-60 seconds after starting)
docker info
```

### 2. Install Cypher Shell (Neo4j CLI)
```bash
# Via Homebrew
brew install cypher-shell

# Verify
cypher-shell --version
```

### 3. Install Python Dependencies
```bash
cd /Users/andrejs/knowledge-graph-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 4. Install Node.js Dependencies (GraphQL API)
```bash
cd api/graphql
npm install
```

## Quick Start

### Step 1: Start Neo4j
```bash
cd /Users/andrejs/knowledge-graph-platform
make start

# Or manually:
cd infra/graph
docker compose up -d
```

**Verification**:
- Neo4j Browser: http://localhost:7474
- Bolt endpoint: bolt://localhost:7687
- Credentials: `neo4j` / `test1234`

### Step 2: Apply Schema
```bash
make apply-schema

# Or manually:
cat schema/init-schema.cypher | cypher-shell -u neo4j -p test1234
```

### Step 3: Load Seed Data
```bash
make seed

# Or manually:
cat schema/seed-data.cypher | cypher-shell -u neo4j -p test1234
```

### Step 4: Verify Installation
```bash
# Connect to Neo4j shell
make neo4j-shell

# Run test query
MATCH (n) RETURN labels(n) AS type, count(*) AS count;

# Should show:
# Project: 2, Tool: 1, Configuration: 1, Pattern: 2
```

## Development Workflow

### Daily Use
```bash
# Start services
make start

# Check graph health
make health

# Visualize
make viz
open kg-viz.html

# Stop services
make stop
```

### Before Major Changes
```bash
# Create snapshot
make snapshot
# Or with custom name:
python scripts/kg/kg-snapshot.py save "pre-refactor-$(date +%Y%m%d)"
```

### After Changes
```bash
# Run health check
make health

# Verify no broken relations
# Health score should be >90%
```

## Troubleshooting

### Docker Not Starting
```bash
# Check if Docker Desktop is running
ps aux | grep -i docker

# If not, start manually
open -a Docker

# Wait 30-60 seconds, then verify
docker info
```

### Neo4j Connection Failed
```bash
# Check container status
docker ps | grep neo4j

# Check logs
docker logs kg-neo4j

# Restart
make restart
```

### Cypher Shell Connection Refused
```bash
# Ensure Neo4j is running
docker ps | grep neo4j

# Wait 10 seconds after starting
sleep 10
cypher-shell -u neo4j -p test1234
```

### Port Already in Use
```bash
# Check what's using ports 7474 or 7687
lsof -i :7474
lsof -i :7687

# Stop conflicting service or change ports in docker-compose.yml
```

## Directory Structure Post-Setup

```
knowledge-graph-platform/
├── .git/                     # Git repository
├── venv/                     # Python virtual environment
├── api/graphql/node_modules/ # Node dependencies
├── infra/graph/neo4j/        # Neo4j data (gitignored)
│   ├── data/                 # Graph database
│   ├── logs/                 # Server logs
│   └── plugins/              # APOC and plugins
└── kg-viz.html               # Generated visualization (gitignored)
```

## Performance Tips (M3 Max)

### Neo4j Memory Tuning
Configured in `docker-compose.yml`:
- Heap: 1G initial, 2G max
- Page cache: 1G
- Good for development workloads

For production (adjust based on dataset size):
- Heap: 4-8G
- Page cache: 16-32G  
- Enable monitoring: NEO4J_metrics_enabled=true

### Python ETL Optimization
- Use 16 workers for parallel ingestion (M3 Max has 16 cores)
- Batch size: 1000-5000 records per transaction
- Use `UNWIND` for bulk inserts (10x faster than individual queries)

## Next Steps

1. Complete setup above
2. Read [Architecture Guide](docs/ARCHITECTURE.md) (to be created)
3. Explore schema: `cat schema/init-schema.cypher`
4. Check seed data: `cat schema/seed-data.cypher`
5. Run health check: `make health`

## Resources

- Neo4j Docs: https://neo4j.com/docs/
- Cypher Manual: https://neo4j.com/docs/cypher-manual/
- @neo4j/graphql: https://neo4j.com/docs/graphql-manual/
- APOC Docs: https://neo4j.com/docs/apoc/

---

**Setup Status**: Ready for development after Docker Desktop is running
