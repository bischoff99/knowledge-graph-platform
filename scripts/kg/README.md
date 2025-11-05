# Knowledge Graph Management Scripts

Comprehensive tooling for managing, monitoring, and maintaining the MCP Knowledge Graph.

## 📚 Available Scripts

### 1. Health Monitoring (`kg-health-check.py`)

**Purpose**: Monitor graph quality and detect issues

**Features**:
- Entity size validation (optimal: 5-8 observations)
- Broken relation detection
- Stale data identification (>90 days old)
- Redundancy detection
- Entity type consistency checking
- Overall health scoring

**Usage**:
```bash
python scripts/kg/kg-health-check.py
```

**Output**: Comprehensive health report with statistics, issues, warnings, and recommendations

---

### 2. Test Result Parser (`test-result-parser.py`)

**Purpose**: Auto-update knowledge graph with test results

**Features**:
- Parses pytest output
- Extracts pass/fail statistics
- Calculates test duration
- Generates trend observations
- Determines if update is significant

**Usage**:
```bash
pytest tests/ -v > output.txt
python scripts/kg/test-result-parser.py output.txt
```

**Auto-integration**: Can be called from git hooks for automatic updates

---

### 3. Git Hook (`post-commit-hook.sh`)

**Purpose**: Automatically update graph on git commits

**Features**:
- Detects commit type (feat, fix, perf, refactor)
- Tracks file changes
- Triggers test parser for test commits
- Records significant changes

**Installation**:
```bash
cp scripts/kg/post-commit-hook.sh .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

**Triggers on**:
- `feat:` commits → Feature tracking
- `fix:` commits → Bug fix logging
- `perf:` commits → Performance improvements
- `test:` commits → Run test parser

---

### 4. Visualization (`kg-visualize.py`)

**Purpose**: Generate interactive graph visualization

**Features**:
- D3.js force-directed graph
- Interactive node exploration
- Color-coded entity types
- Node size based on observation count
- Relationship visualization

**Usage**:
```bash
python scripts/kg/kg-visualize.py
# Opens kg-viz.html in browser
```

**Output**: Interactive HTML visualization

---

### 5. Snapshot System (`kg-snapshot.py`)

**Purpose**: Backup and restore graph states

**Features**:
- Save graph snapshots with metadata
- List all available snapshots
- Restore from any snapshot
- Delete old snapshots
- Automatic timestamping

**Usage**:
```bash
# Save snapshot
python scripts/kg/kg-snapshot.py save "pre-refactor-2025-11-05"

# List snapshots
python scripts/kg/kg-snapshot.py list

# Restore snapshot
python scripts/kg/kg-snapshot.py restore "pre-refactor-2025-11-05"

# Delete snapshot
python scripts/kg/kg-snapshot.py delete "old-snapshot"
```

**Storage**: `~/.kg-snapshots/`

---

## 🚀 Quick Start

### Run Health Check
```bash
python scripts/kg/kg-health-check.py
```

### Create Snapshot Before Changes
```bash
python scripts/kg/kg-snapshot.py save "before-$(date +%Y%m%d)"
```

### Visualize Graph
```bash
python scripts/kg/kg-visualize.py
open kg-viz.html
```

---

## 🔄 Automation Workflow

### Recommended Setup

1. **Install git hook**:
```bash
cp scripts/kg/post-commit-hook.sh .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

2. **Weekly health checks** (add to crontab):
```bash
0 9 * * 1 cd /path/to/project && python scripts/kg/kg-health-check.py
```

3. **Pre-release snapshot**:
```bash
# Add to release process
python scripts/kg/kg-snapshot.py save "release-$(git describe --tags)"
```

---

## 📊 Metadata Format

All scripts understand the metadata format used in observations:

```python
"Meta:last_updated:2025-11-05"  # Timestamp
"Meta:status:production"         # Status
"Meta:criticality:high"          # Importance
"Meta:tags:m3-max,performance"   # Tags (comma-separated)

"Timeline:event:date"            # Timeline events
"Health:metric:value"            # Health metrics
"Performance:metric:value"       # Performance metrics
"Pattern:description"            # Pattern information
```

---

## 🎯 Best Practices

1. **Run health check weekly** to catch issues early
2. **Create snapshots before major changes** for easy rollback
3. **Use git hooks for automatic updates** to keep graph current
4. **Visualize graph monthly** to understand structure
5. **Review stale entities quarterly** and update or archive

---

## 🔧 Requirements

- Python 3.8+
- No external dependencies (uses stdlib only)
- MCP Memory server for live data access
- D3.js (CDN) for visualization

---

## 📝 Configuration

Scripts can be configured via environment variables:

```bash
export KG_SNAPSHOT_DIR="$HOME/.kg-snapshots"
export KG_HEALTH_THRESHOLD_DAYS=90
export KG_MAX_OBSERVATIONS=12
```

---

## 🤝 Integration with MCP Memory

All scripts are designed to work with MCP Memory server. In production:

1. Connect to MCP server
2. Fetch graph data via `mcp_memory_read_graph`
3. Process with scripts
4. Update via `mcp_memory_add_observations`

Example integration:
```python
# Fetch graph
graph = mcp_memory_read_graph()

# Run health check
checker = KGHealthChecker()
score = checker.generate_report(graph['entities'], graph['relations'])

# Save snapshot if needed
if score < 75:
    snapshot = KGSnapshot()
    snapshot.save(graph, f"pre-fix-{datetime.now().strftime('%Y%m%d')}")
```

---

## 📈 Future Enhancements

- [ ] Natural language query interface
- [ ] Automated fix suggestions
- [ ] ML-powered similarity detection
- [ ] Performance trend tracking
- [ ] Multi-graph support
- [ ] Export to Neo4j/GraphQL

---

**Created**: 2025-11-05  
**Version**: 1.0  
**Maintainer**: Knowledge Graph System
