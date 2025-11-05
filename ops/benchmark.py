#!/usr/bin/env python3
"""
Knowledge Graph Performance Benchmarks
Tests read/write throughput, query performance, index effectiveness
"""

import time
import asyncio
from statistics import mean, median
from neo4j import GraphDatabase


class KGBenchmark:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def benchmark_write_throughput(self, num_nodes: int = 10000, batch_size: int = 1000):
        """Test bulk write performance with UNWIND"""
        print(f"\n📝 Write Throughput Test ({num_nodes} nodes, batch_size={batch_size})")
        
        start = time.time()
        
        with self.driver.session() as session:
            batches = num_nodes // batch_size
            for i in range(batches):
                batch = [
                    {"id": f"bench-{i*batch_size + j}", "name": f"Node {i*batch_size + j}", "value": j}
                    for j in range(batch_size)
                ]
                
                session.run("""
                    UNWIND $batch AS row
                    CREATE (n:BenchmarkNode {id: row.id, name: row.name, value: row.value})
                """, batch=batch)
        
        duration = time.time() - start
        throughput = num_nodes / duration
        
        print(f"✅ Created {num_nodes} nodes in {duration:.2f}s")
        print(f"   Throughput: {throughput:.1f} nodes/sec")
        
        # Cleanup
        with self.driver.session() as session:
            session.run("MATCH (n:BenchmarkNode) DELETE n")
        
        return {"nodes": num_nodes, "duration": duration, "throughput": throughput}
    
    def benchmark_read_performance(self, num_queries: int = 1000):
        """Test read query latency"""
        print(f"\n📖 Read Performance Test ({num_queries} queries)")
        
        # Seed data
        with self.driver.session() as session:
            session.run("""
                UNWIND range(1, 100) AS i
                CREATE (n:BenchmarkNode {id: 'read-' + toString(i), value: i})
            """)
        
        latencies = []
        
        with self.driver.session() as session:
            for i in range(num_queries):
                start = time.time()
                session.run("MATCH (n:BenchmarkNode {id: 'read-50'}) RETURN n")
                latencies.append((time.time() - start) * 1000)  # ms
        
        # Cleanup
        with self.driver.session() as session:
            session.run("MATCH (n:BenchmarkNode) DELETE n")
        
        print(f"✅ Executed {num_queries} read queries")
        print(f"   P50 latency: {median(latencies):.2f}ms")
        print(f"   P95 latency: {sorted(latencies)[int(num_queries * 0.95)]:.2f}ms")
        print(f"   Avg latency: {mean(latencies):.2f}ms")
        
        return {"queries": num_queries, "p50": median(latencies), "p95": sorted(latencies)[int(num_queries * 0.95)]}
    
    def benchmark_index_effectiveness(self):
        """Compare indexed vs non-indexed query performance"""
        print(f"\n🔍 Index Effectiveness Test")
        
        # Create test data (50k nodes)
        print("  Creating 50k nodes...")
        with self.driver.session() as session:
            for i in range(50):
                batch = [{"id": f"idx-{i*1000 + j}", "value": j} for j in range(1000)]
                session.run("""
                    UNWIND $batch AS row
                    CREATE (n:IndexTest {id: row.id, value: row.value})
                """, batch=batch)
        
        # Query without index
        start = time.time()
        with self.driver.session() as session:
            session.run("MATCH (n:IndexTest {id: 'idx-25000'}) RETURN n")
        no_index_time = (time.time() - start) * 1000
        
        # Create index
        with self.driver.session() as session:
            session.run("CREATE INDEX idx_test_id IF NOT EXISTS FOR (n:IndexTest) ON (n.id)")
        
        time.sleep(2)  # Wait for index build
        
        # Query with index
        start = time.time()
        with self.driver.session() as session:
            session.run("MATCH (n:IndexTest {id: 'idx-25000'}) RETURN n")
        with_index_time = (time.time() - start) * 1000
        
        # Cleanup
        with self.driver.session() as session:
            session.run("MATCH (n:IndexTest) DELETE n")
            session.run("DROP INDEX idx_test_id IF EXISTS")
        
        speedup = no_index_time / with_index_time if with_index_time > 0 else 0
        
        print(f"✅ Without index: {no_index_time:.2f}ms")
        print(f"✅ With index: {with_index_time:.2f}ms")
        print(f"   Speedup: {speedup:.1f}x")
        
        return {"no_index_ms": no_index_time, "with_index_ms": with_index_time, "speedup": speedup}
    
    def run_all_benchmarks(self):
        """Execute full benchmark suite"""
        print("=" * 70)
        print("KNOWLEDGE GRAPH PERFORMANCE BENCHMARKS")
        print("=" * 70)
        
        results = {}
        results['write'] = self.benchmark_write_throughput()
        results['read'] = self.benchmark_read_performance()
        results['index'] = self.benchmark_index_effectiveness()
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Write throughput: {results['write']['throughput']:.1f} nodes/sec")
        print(f"Read P50 latency: {results['read']['p50']:.2f}ms")
        print(f"Index speedup: {results['index']['speedup']:.1f}x")
        print("=" * 70)
        
        return results


if __name__ == '__main__':
    bench = KGBenchmark(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test1234"
    )
    
    bench.run_all_benchmarks()
    bench.driver.close()
