#!/usr/bin/env python3
"""
Knowledge Graph Snapshot System
Save and restore graph states for backup/rollback
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


class KGSnapshot:
    def __init__(self, snapshot_dir=None):
        if snapshot_dir is None:
            self.snapshot_dir = Path.home() / '.kg-snapshots'
        else:
            self.snapshot_dir = Path(snapshot_dir)
        
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, graph_data, name=None):
        """Save current graph state"""
        if name is None:
            name = f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        snapshot_file = self.snapshot_dir / f"{name}.json"
        
        with open(snapshot_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        # Also save metadata
        metadata = {
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'entity_count': len(graph_data.get('entities', [])),
            'relation_count': len(graph_data.get('relations', []))
        }
        
        meta_file = self.snapshot_dir / f"{name}.meta.json"
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Snapshot saved: {name}")
        print(f"   Location: {snapshot_file}")
        print(f"   Entities: {metadata['entity_count']}")
        print(f"   Relations: {metadata['relation_count']}")
        
        return snapshot_file
    
    def list_snapshots(self):
        """List all available snapshots"""
        snapshots = []
        for meta_file in sorted(self.snapshot_dir.glob("*.meta.json")):
            with open(meta_file) as f:
                metadata = json.load(f)
                snapshots.append(metadata)
        
        if not snapshots:
            print("No snapshots found")
            return []
        
        print(f"\n📸 Available Snapshots ({len(snapshots)}):")
        print("-" * 80)
        for snap in snapshots:
            print(f"  {snap['name']}")
            print(f"    Date: {snap['timestamp'][:19]}")
            print(f"    Size: {snap['entity_count']} entities, {snap['relation_count']} relations")
            print()
        
        return snapshots
    
    def restore(self, name):
        """Restore graph from snapshot"""
        snapshot_file = self.snapshot_dir / f"{name}.json"
        
        if not snapshot_file.exists():
            print(f"❌ Snapshot not found: {name}")
            return None
        
        with open(snapshot_file) as f:
            graph_data = json.load(f)
        
        print(f"✅ Snapshot restored: {name}")
        print(f"   Entities: {len(graph_data.get('entities', []))}")
        print(f"   Relations: {len(graph_data.get('relations', []))}")
        print("\n⚠️  Note: You must manually update MCP memory with this data")
        
        return graph_data
    
    def delete(self, name):
        """Delete a snapshot"""
        snapshot_file = self.snapshot_dir / f"{name}.json"
        meta_file = self.snapshot_dir / f"{name}.meta.json"
        
        if snapshot_file.exists():
            snapshot_file.unlink()
        if meta_file.exists():
            meta_file.unlink()
        
        print(f"🗑️  Snapshot deleted: {name}")


if __name__ == '__main__':
    import sys
    
    snapshot = KGSnapshot()
    
    if len(sys.argv) < 2:
        print("Knowledge Graph Snapshot System")
        print("\nUsage:")
        print("  python kg-snapshot.py save [name]      # Save current state")
        print("  python kg-snapshot.py list             # List snapshots")
        print("  python kg-snapshot.py restore <name>   # Restore from snapshot")
        print("  python kg-snapshot.py delete <name>    # Delete snapshot")
        print(f"\nSnapshots stored in: {snapshot.snapshot_dir}")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'list':
        snapshot.list_snapshots()
    elif command == 'save':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        print("Note: Connect to MCP memory to save actual graph data")
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("Error: Provide snapshot name")
            sys.exit(1)
        snapshot.restore(sys.argv[2])
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Error: Provide snapshot name")
            sys.exit(1)
        snapshot.delete(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
