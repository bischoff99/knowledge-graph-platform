.PHONY: help install start stop restart neo4j-shell apply-schema seed health viz snapshot clean

help:
	@echo "Knowledge Graph Platform - Make Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies (Python + Node.js)"
	@echo "  make start          Start Neo4j (docker compose)"
	@echo ""
	@echo "Database:"
	@echo "  make neo4j-shell    Connect to Neo4j cypher-shell"
	@echo "  make apply-schema   Apply schema (constraints, indexes)"
	@echo "  make seed           Load seed data"
	@echo ""
	@echo "Operations:"
	@echo "  make health         Run graph health check"
	@echo "  make viz            Generate visualization"
	@echo "  make snapshot       Create backup snapshot"
	@echo ""
	@echo "Management:"
	@echo "  make stop           Stop Neo4j"
	@echo "  make restart        Restart Neo4j"
	@echo "  make clean          Clean data volumes (DESTRUCTIVE)"

install:
	@echo "📦 Installing dependencies..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	cd api/graphql && npm install

start:
	@echo "🚀 Starting Neo4j..."
	cd infra/graph && docker compose up -d
	@echo "⏳ Waiting for Neo4j to be ready..."
	@sleep 10
	@echo "✅ Neo4j running at http://localhost:7474"
	@echo "   Username: neo4j"
	@echo "   Password: test1234"

stop:
	@echo "🛑 Stopping Neo4j..."
	cd infra/graph && docker compose down

restart: stop start

neo4j-shell:
	@echo "🔌 Connecting to Neo4j..."
	cypher-shell -u neo4j -p test1234

apply-schema:
	@echo "📐 Applying schema..."
	cat schema/init-schema.cypher | cypher-shell -u neo4j -p test1234
	@echo "✅ Schema applied"

seed:
	@echo "🌱 Loading seed data..."
	cat schema/seed-data.cypher | cypher-shell -u neo4j -p test1234
	@echo "✅ Seed data loaded"

health:
	@echo "🏥 Running health check..."
	python scripts/kg/kg-health-check.py

viz:
	@echo "📊 Generating visualization..."
	python scripts/kg/kg-visualize.py
	@echo "✅ Open kg-viz.html in browser"

snapshot:
	@echo "📸 Creating snapshot..."
	python scripts/kg/kg-snapshot.py save "snapshot-$$(date +%Y%m%d-%H%M%S)"

clean:
	@echo "⚠️  WARNING: This will delete all graph data!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	cd infra/graph && docker compose down -v
	@echo "🗑️  Data volumes deleted"
