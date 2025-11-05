# Security Hardening Guide

## Authentication & Access Control

### Neo4j Security

**Default credentials** (change immediately):
```bash
# Connect and change password
cypher-shell -u neo4j -p test1234
:ALTER USER neo4j SET PASSWORD 'strong-password-here';
```

**Create read-only user**:
```cypher
CREATE USER reader SET PASSWORD 'reader-password' CHANGE NOT REQUIRED;
GRANT ROLE reader TO reader;
```

**Create application user**:
```cypher
CREATE USER kg_api SET PASSWORD 'api-password' CHANGE NOT REQUIRED;
GRANT ROLE PUBLIC TO kg_api;
GRANT MATCH {*} ON GRAPH * TO kg_api;
DENY WRITE ON GRAPH * TO kg_api;
```

### API Security

**Environment variables** (never commit):
```bash
# .env (gitignored)
NEO4J_PASSWORD=strong-password
OPENAI_API_KEY=sk-...
JWT_SECRET=random-secret-key
```

**Rate limiting** (FastAPI):
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/search")
@limiter.limit("10/minute")
async def search(q: str):
    ...
```

**CORS restrictions**:
```python
# Restrict to known origins in production
allow_origins=["https://your-frontend.com"]
```

## Network Security

### TLS/SSL for Neo4j

Update `docker-compose.yml`:
```yaml
environment:
  - NEO4J_dbms_connector_bolt_tls__level=REQUIRED
  - NEO4J_dbms_ssl_policy_bolt_enabled=true
volumes:
  - ./certs:/var/lib/neo4j/certificates
```

Generate certificates:
```bash
mkdir -p infra/graph/certs
# Use Let's Encrypt or self-signed for development
```

### Firewall Rules

**macOS**:
```bash
# Allow only localhost access
# Neo4j ports 7474, 7687 should NOT be exposed publicly
```

**Production** (K8s NetworkPolicy):
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: neo4j-access
spec:
  podSelector:
    matchLabels:
      app: neo4j
  ingress:
    - from:
      - podSelector:
          matchLabels:
            role: api
```

## Data Security

### PII Handling

**Encrypt sensitive properties**:
```cypher
// Use apoc.util.sha256 or external encryption service
CREATE (n:User {
  email_hash: apoc.util.sha256(['user@example.com']),
  // Never store plaintext PII
})
```

**Data masking for non-prod**:
```cypher
// Anonymize data in dev/staging
MATCH (n:User)
SET n.email = 'user' + id(n) + '@example.com'
```

### Audit Logging

Enable Neo4j security logs:
```yaml
environment:
  - NEO4J_dbms_security_logs_enabled=true
  - NEO4J_dbms_logs_security_level=INFO
```

Track API access:
```python
# FastAPI middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url} - User: {request.headers.get('X-User-ID')}")
    response = await call_next(request)
    return response
```

## Input Validation

### Cypher Injection Prevention

**Never interpolate user input**:
```python
# ❌ DANGEROUS
query = f"MATCH (n {{name: '{user_input}'}}) RETURN n"

# ✅ SAFE - use parameters
query = "MATCH (n {name: $name}) RETURN n"
session.run(query, name=user_input)
```

### Schema validation

Use Pydantic for request validation:
```python
class EntityQuery(BaseModel):
    entity_id: str = Field(..., regex=r'^[a-zA-Z0-9\-_]+$', max_length=100)
    depth: int = Field(1, ge=1, le=5)
```

## Least Privilege

### Application Permissions

- **API user**: Read-only + specific write procedures only
- **ETL user**: Write access, no admin
- **Admin user**: Full access, use sparingly, rotate credentials

### Docker Security

```yaml
# Run as non-root user
user: "7474:7474"  # Neo4j user/group

# Read-only root filesystem
read_only: true
tmpfs:
  - /tmp
```

## Secrets Management

### Development
```bash
# Use environment variables, not hardcoded values
export NEO4J_PASSWORD=$(openssl rand -base64 32)
```

### Production

Use secrets manager:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets (with encryption at rest)

```yaml
# K8s example
env:
  - name: NEO4J_PASSWORD
    valueFrom:
      secretKeyRef:
        name: neo4j-credentials
        key: password
```

## Monitoring & Alerts

### Health Checks
```bash
# Alert on failures
*/5 * * * * curl -f http://localhost:8000/health || alert-script.sh
```

### Metrics
```python
# Track suspicious patterns
- Excessive failed login attempts
- Unusual query patterns
- Large data exports
- Schema modifications
```

## Incident Response

### Compromise detected
1. Rotate all credentials immediately
2. Review audit logs for breach scope
3. Snapshot current state (forensics)
4. Restore from known-good backup
5. Apply security patches
6. Document incident and mitigations

### Backup testing
```bash
# Monthly: Test restore procedure
./ops/backup.sh
./ops/restore.sh backups/latest-backup.tar.gz
# Verify data integrity
```

## Compliance

### GDPR (if applicable)
- Implement right to erasure: DELETE operations
- Data retention policies: Automatic purging
- Consent tracking in entity properties

### SOC 2 (if applicable)
- Audit logging enabled
- Access controls documented
- Encryption in transit and at rest
- Regular security reviews

## Security Checklist

- [ ] Change default Neo4j password
- [ ] Create least-privilege users for API/ETL
- [ ] Enable TLS for production
- [ ] Implement rate limiting on APIs
- [ ] Add input validation (Pydantic, Cypher params)
- [ ] Configure CORS restrictions
- [ ] Enable audit logging
- [ ] Set up automated backups (daily)
- [ ] Test restore procedure (monthly)
- [ ] Scan dependencies for vulnerabilities (CI)
- [ ] Document incident response plan
- [ ] Rotate credentials quarterly
- [ ] Review access logs weekly

---

**Last Updated**: November 5, 2025  
**Security Contact**: security@your-org.com (update as needed)
