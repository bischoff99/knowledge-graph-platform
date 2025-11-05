# Knowledge Graph Platform

Industry-grade knowledge graph infrastructure for cross-project knowledge management.

## Overview

Production-ready knowledge graph platform managing knowledge across multiple projects:
- **EasyPost MCP** - Shipping automation
- **macossetup** - Development environment
- **Obsidian** - Knowledge management
- **ML Training** - Machine learning experiments

## Stack

- **Graph DB**: Neo4j 5.22 (Property Graph, Cypher)
- **Optional RDF**: Apache Jena Fuseki (SPARQL) 
- **API**: GraphQL (@neo4j/graphql) + REST (FastAPI)
- **Ingestion**: Python ETL (pandas, pydantic)
- **Extraction**: spaCy NER + LLM fallback
- **Deployment**: Docker Compose (dev), Kubernetes (prod)

## Quick Start

### Prerequisites
```bash
# macOS
brew install --cask docker
brew install cypher-shell
```

### Start Neo4j
```bash
cd infra/graph
docker compose up -d
# Neo4j Browser: http://localhost:7474
# Credentials: neo4j/test1234
```

### Verify
```bash
cypher-shell -u neo4j -p test1234
# Run: RETURN "Connected!" AS status;
```

## Directory Structure

```
knowledge-graph-platform/
├── infra/graph/          # Docker Compose, K8s manifests
├── schema/               # Property graph schema, indexes
├── ingestion/            # Python ETL pipelines
├── api/                  # GraphQL + REST gateways
│   ├── graphql/          # @neo4j/graphql server
│   └── rest/             # FastAPI service
├── governance/           # Validation, QA, provenance
├── clients/              # Python + TypeScript clients
├── ops/                  # Backups, migrations, runbooks
├── scripts/kg/           # Health checks, snapshots, viz
└── docs/                 # Architecture, guides
```

## Features

- **Temporal tracking**: All entities versioned with timestamps
- **Auto-updates**: Git hooks, test result parsing
- **Health monitoring**: Automated quality checks (95% score)
- **Visualization**: Interactive D3.js graph explorer
- **Snapshots**: Backup/restore system
- **Pattern reuse**: Cross-project design patterns
- **Semantic search**: FAQ entities, keyword matching

## Scripts

```bash
# Health check
python scripts/kg/kg-health-check.py

# Visualize graph
python scripts/kg/kg-visualize.py
open kg-viz.html

# Create snapshot
python scripts/kg/kg-snapshot.py save "baseline-$(date +%Y%m%d)"

# List snapshots
python scripts/kg/kg-snapshot.py list
```

## Status

- **Entities**: 33
- **Relations**: 38
- **Health Score**: 95% (Excellent)
- **Production Ready**: Yes

## Documentation

- [Upgrade Guide](docs/KNOWLEDGE_GRAPH_UPGRADE_COMPLETE.md)
- [Script Documentation](scripts/kg/README.md)
- [Architecture Decisions](docs/architecture/)

## License

MIT
