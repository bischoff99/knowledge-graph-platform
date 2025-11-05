#!/bin/bash
# Neo4j Backup Script
# Creates timestamped backups and optionally uploads to cloud storage

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="kg-backup-${TIMESTAMP}"

mkdir -p "${BACKUP_DIR}"

echo "🔒 Creating Neo4j backup: ${BACKUP_NAME}"

# Stop Neo4j for consistent backup (or use online backup in Enterprise)
docker compose -f infra/graph/docker-compose.yml stop neo4j

# Copy data directory
echo "📦 Copying data directory..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" infra/graph/neo4j/data

# Restart Neo4j
docker compose -f infra/graph/docker-compose.yml start neo4j

# Backup metadata
cat > "${BACKUP_DIR}/${BACKUP_NAME}.meta.json" << META
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "size_bytes": $(stat -f%z "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" 2>/dev/null || stat -c%s "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"),
  "neo4j_version": "5.22",
  "backup_type": "full"
}
META

echo "✅ Backup complete: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Optional: Upload to S3/GCS
if [ ! -z "$AWS_BACKUP_BUCKET" ]; then
    echo "☁️  Uploading to S3..."
    aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "s3://${AWS_BACKUP_BUCKET}/neo4j-backups/"
fi

# Cleanup old backups (keep last 7 days)
find "${BACKUP_DIR}" -name "kg-backup-*.tar.gz" -mtime +7 -delete

echo "🎯 Backup location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
