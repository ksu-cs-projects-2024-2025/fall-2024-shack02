from flask import Flask, render_template
from pyvis.network import Network
from neo4j import GraphDatabase
from neo4j_query_library import Neo4jQueryEngine
import os


class GraphVisualizer:
    def __init__(self):
        return

    #Helper function for calculating correct edge weight based on query
    def get_edge_weight(self, query_type, edge):
        weight = 1
        if query_type == "essential_track":
            distance = edge['properties']['distance']
            if distance != 0:
                weight = 1 / distance
            else:
                weight = 100
        return weight

    #Helper function for displaying correct edge labels based on query
    def get_edge_label(self, query_type, edge, i):
        label = edge['type']
        if query_type == "essential_track":
            label = str(i + 1)
        return label

    #Takes the graph data and add the nodes and edges to a pyvis network
    def base_visualizer_v2(self, graph_data):
        net = Network(height="600px", width="100%", notebook=False)
        for node in graph_data["nodes"]:
            node_information = "\n".join(f"{key}: {value}" for key, value in node['properties'].items())
            print(node)
            net.add_node(label = node['properties']['name'], n_id = str(node['id']), group=node['labels'][0], title=node_information)
        for i,edge in enumerate(graph_data["edges"]):
            edge_information = "\n".join(f"{key}: {value}" for key, value in edge['properties'].items())
            print(edge)
            net.add_edge(source=edge['source'], to =edge['target'], label=self.get_edge_label(graph_data['query_name'], edge, i), edge_data=edge['properties'], value=self.get_edge_weight(graph_data["query_name"], edge), title = edge_information)
        net.set_options("""
            var options = {
            "nodes": {
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "color": {
                "highlight": {
                    "border": "black",
                    "background": "orange"
                }
                }
            },
            "edges": {
                "color": {
                "inherit": true
                },
                "smooth": {
                "type": "continuous"
                }
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "multiselect": true
            },
            "physics": {
                "enabled": true,
                "barnesHut": {
                "gravitationalConstant": -2000,
                "centralGravity": 0.3,
                "springLength": 100,
                "springConstant": 0.1
                },
                "forceAtlas2Based": {
                "gravitationalConstant": -500,
                "centralGravity": 0.01,
                "springLength": 50,
                "springConstant": 0.1
                },
                "repulsion": {
                "centralGravity": 0.0,
                "springLength": 100,
                "springConstant": 0.1,
                "damping": 0.09
                }
            }
            }
        """)
        return net

    #Function for making the pyvis network and saving it into a static html file for displaying via Flask
    def create_network(self, graph_data):
        config = {"query": graph_data['query_name']}
        net = self.base_visualizer_v2(graph_data)
        html = net.generate_html(f"{graph_data['query_name']}.html", notebook=False)
        with open(fr"src\static\{graph_data['query_name']}_network.html", 'w') as file:
            file.write(html)
