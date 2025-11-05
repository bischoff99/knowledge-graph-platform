// Seed Data - Knowledge Graph Platform
// Populates initial entities and relationships
// Created: 2025-11-05

// ========================================
// CORE INFRASTRUCTURE
// ========================================

// Desktop Commander MCP (critical infrastructure)
CREATE (dc:Tool:Infrastructure {
  id: 'desktop-commander-mcp',
  name: 'Desktop Commander MCP',
  status: 'stable',
  criticality: 'critical',
  tags: ['infrastructure', 'mcp-server', 'core'],
  last_updated: datetime('2025-10-20'),
  created_at: datetime('2025-09-01'),
  description: 'MCP server for file system operations and terminal commands',
  line_read_limit: 500,
  line_write_limit: 30
});

// M3 Max Hardware Setup
CREATE (hw:Configuration:Hardware {
  id: 'user-m3-max-setup',
  name: 'User M3 Max Setup',
  status: 'stable',
  criticality: 'critical',
  tags: ['hardware', 'm3-max', 'baseline'],
  last_updated: datetime('2025-10-15'),
  cpu_cores: 16,
  cpu_p_cores: 12,
  cpu_e_cores: 4,
  gpu_cores: 40,
  ram_gb: 128,
  ssd_tb: 8,
  description: 'M3 Max MacBook Pro hardware baseline'
});

// ========================================
// PROJECTS
// ========================================

// EasyPost MCP Project
CREATE (ep:Project {
  id: 'easypost-mcp-project',
  name: 'EasyPost MCP Project',
  status: 'production',
  criticality: 'high',
  tags: ['production', 'shipping', 'fastapi', 'react'],
  last_verified: datetime('2025-11-05'),
  created_at: datetime('2025-10-01'),
  location: '/Users/andrejs/easypost-mcp-project',
  stack_backend: 'FastAPI Python 3.12',
  stack_frontend: 'React 18',
  stack_database: 'PostgreSQL',
  test_pass_rate: 97.3,
  grade: 'A'
});

// macossetup Project
CREATE (ms:Project {
  id: 'macossetup',
  name: 'macossetup',
  status: 'active',
  criticality: 'high',
  tags: ['dev-environment', 'macos', 'm3-max'],
  last_updated: datetime('2025-10-01'),
  location: '/Users/andrejs/macossetup',
  description: 'M3 Max optimized development environment'
});

// ========================================
// DESIGN PATTERNS
// ========================================

// M3 Max Parallel Processing Pattern
CREATE (pp:Pattern {
  id: 'm3-max-parallel-pattern',
  name: 'M3 Max Parallel Processing Pattern',
  status: 'proven',
  criticality: 'high',
  tags: ['m3-max', 'pattern', 'performance', 'reusable'],
  last_updated: datetime('2025-11-05'),
  created_at: datetime('2025-11-05'),
  formula: 'workers = min(32, cpu_count * 2)',
  proven_speedup: '10x',
  applies_to: 'pytest, bulk operations, data processing, API calls'
});

// Async-First Architecture Pattern
CREATE (ap:Pattern {
  id: 'async-first-pattern',
  name: 'Async-First Architecture Pattern',
  status: 'proven',
  tags: ['pattern', 'async', 'architecture', 'best-practice'],
  created_at: datetime('2025-11-05'),
  description: 'All I/O operations use async/await',
  performance_gain: '2-4x with uvloop',
  database_lib: 'asyncpg',
  http_lib: 'httpx or aiohttp'
});

// ========================================
// RELATIONSHIPS
// ========================================

// Dependencies
MATCH (ep:Project {id: 'easypost-mcp-project'}), (dc:Tool {id: 'desktop-commander-mcp'})
CREATE (ep)-[:DEPENDS_ON_CRITICAL {established: datetime('2025-10-01')}]->(dc);

MATCH (ms:Project {id: 'macossetup'}), (dc:Tool {id: 'desktop-commander-mcp'})
CREATE (ms)-[:DEPENDS_ON_CRITICAL {established: datetime('2025-09-15')}]->(dc);

// Hardware optimization
MATCH (ep:Project {id: 'easypost-mcp-project'}), (hw:Configuration {id: 'user-m3-max-setup'})
CREATE (ep)-[:OPTIMIZED_FOR {applied: datetime('2025-10-15')}]->(hw);

MATCH (pp:Pattern {id: 'm3-max-parallel-pattern'}), (hw:Configuration {id: 'user-m3-max-setup'})
CREATE (pp)-[:OPTIMIZED_FOR {defined: datetime('2025-11-05')}]->(hw);

// Pattern application
MATCH (ep:Project {id: 'easypost-mcp-project'}), (pp:Pattern {id: 'm3-max-parallel-pattern'})
CREATE (ep)-[:IMPLEMENTS_PATTERN {since: datetime('2025-10-15')}]->(pp);

MATCH (ep:Project {id: 'easypost-mcp-project'}), (ap:Pattern {id: 'async-first-pattern'})
CREATE (ep)-[:IMPLEMENTS_PATTERN {since: datetime('2025-10-10')}]->(ap);

// ========================================
// VERIFICATION QUERIES
// ========================================

// Count entities
// MATCH (n) RETURN labels(n) AS type, count(*) AS count ORDER BY count DESC;

// Show all projects
// MATCH (p:Project) RETURN p.name, p.status, p.criticality, p.tags;

// Show critical dependencies
// MATCH (p)-[r:DEPENDS_ON_CRITICAL]->(d) RETURN p.name, d.name, r.established;

// Show patterns and implementations
// MATCH (proj:Project)-[:IMPLEMENTS_PATTERN]->(pattern:Pattern) RETURN proj.name, pattern.name;
