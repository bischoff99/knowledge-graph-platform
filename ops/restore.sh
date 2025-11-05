#!/bin/bash
# Neo4j Restore Script

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup-file.tar.gz>"
    echo "Available backups:"
    ls -lh backups/*.tar.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

echo "⚠️  WARNING: This will replace all current graph data!"
read -p "Continue? (yes/no): " confirm
[ "$confirm" != "yes" ] && exit 0

# Stop Neo4j
echo "🛑 Stopping Neo4j..."
cd infra/graph && docker compose down

# Remove existing data
echo "🗑️  Removing existing data..."
rm -rf infra/graph/neo4j/data/*

# Extract backup
echo "📦 Restoring from backup..."
tar -xzf "${BACKUP_FILE}" -C .

# Start Neo4j
echo "🚀 Starting Neo4j..."
docker compose up -d

echo "✅ Restore complete from: ${BACKUP_FILE}"
