#!/usr/bin/env python3
"""
Knowledge Graph Visualization
Generates interactive HTML visualization using D3.js
"""

import json
from pathlib import Path


def generate_html_viz(entities, relations, output_file="kg-viz.html"):
    """Generate D3.js force-directed graph visualization"""
    
    # Convert to D3 format
    nodes = []
    for i, entity in enumerate(entities):
        node = {
            'id': entity['name'],
            'name': entity['name'],
            'type': entity.get('entityType', 'unknown'),
            'obs_count': len(entity.get('observations', [])),
            'group': hash(entity.get('entityType', '')) % 10
        }
        nodes.append(node)
    
    links = []
    for rel in relations:
        links.append({
            'source': rel['from'],
            'target': rel['to'],
            'type': rel['relationType'],
            'value': 1
        })
    
    graph_data = {'nodes': nodes, 'links': links}
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Knowledge Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; }}
        #graph {{ width: 100vw; height: 100vh; }}
        .node {{ cursor: pointer; }}
        .node circle {{ stroke: #fff; stroke-width: 2px; }}
        .link {{ stroke: #999; stroke-opacity: 0.6; }}
        #info {{ position: absolute; top: 10px; left: 10px; 
                background: white; padding: 15px; border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .legend {{ position: absolute; bottom: 20px; right: 20px;
                  background: white; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Knowledge Graph</h3>
        <p>Entities: {len(nodes)} | Relations: {len(links)}</p>
        <p>Click nodes for details</p>
    </div>
    <svg id="graph"></svg>
    <script>
        const data = {json.dumps(graph_data, indent=2)};
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", 2);
        
        const node = svg.append("g")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("r", d => Math.sqrt(d.obs_count) * 3 + 5)
            .attr("fill", d => d3.schemeCategory10[d.group]);
        
        node.append("text")
            .text(d => d.name.split(' ')[0])
            .attr("x", 12)
            .attr("y", 3)
            .style("font-size", "10px");
        
        node.on("click", (event, d) => {{
            alert(`${{d.name}}\\nType: ${{d.type}}\\nObservations: ${{d.obs_count}}`);
        }});
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>'''
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Visualization saved to {output_file}")
    print(f"Open in browser: file://{Path(output_file).absolute()}")


if __name__ == '__main__':
    print("Knowledge Graph Visualizer")
    print("Usage: python kg-visualize.py")
    print("Note: Connect to MCP memory to generate visualization")
