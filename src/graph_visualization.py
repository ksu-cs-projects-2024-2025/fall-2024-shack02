from flask import Flask, render_template
from pyvis.network import Network
from neo4j import GraphDatabase
from neo4j_query_library import Neo4jQueryEngine
import os
import json

#This class is partially the view for the GrooveMapper application. It takes graph data from the query engine and constructs a pyvis graph to be displayed via the flask
class GraphVisualizer:
    def __init__(self):
        return

    #Helper function for calculating correct edge weight based on query
    def get_edge_weight(self, query_type, edge):
        weight = 1
        if (query_type == "essential_track") or (query_type == "artist_recommender") or (query_type == "track_recommender"):
            distance = edge['properties'].get('distance')
            if distance is None:
                weight = 1
            elif distance != 0:
                weight = 1 / distance
            else:
                weight = 100
        return weight

    #Helper function for displaying correct edge labels based on query
    def get_edge_label(self, query_type, edge, i):
        label = edge['type']
        if (query_type == "essential_track") or (query_type == "artist_recommender") or ((query_type == "track_recommender") and (edge['type'] == 'DISTANCE')):
            label = str(i + 1)
        elif (query_type == "genre_overlap"):
            label = None
        return label

    #This class customizes the graph display options based on the query type.
    def node_display_options(self, query_name):
        options = {
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
                "inherit": True
            },
            "smooth": {
                "type": "continuous"
            },
            "length": 200
        },
        "interaction": {
            "hover": True,
            "navigationButtons": True,
            "multiselect": True
        },
        "physics": {
            "enabled": True,
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
        if (query_name == "shortest_path"):
            options["physics"] = {
            "enabled": False
            }
            options["layout"] = {
                "hierarchical": {
                    "enabled": True,
                    "direction": "LR",
                    "sortMethod": "directed"
                }
            }
            options["edges"]["length"] = 300
        elif (query_name == "genre_overlap"):
            options["physics"] = {
            "enabled": True
            }
            options["layout"] = {
                "hierarchical": {
                    "enabled": False,
                    "direction": "DU",
                    "sortMethod": "directed"
                }
            }
            options["edges"]["length"] = 300
        elif (query_name == "home"):
            options["physics"] = {
            "enabled": True
            }
            options["layout"] = {
            "randomSeed": 2, 
            "improvedLayout": True,
            "hierarchicalRepulsion": {
                "nodeDistance": 150, 
                "springLength": 100, 
            },
            "circular": {
                "enabled": True, 
                "sortMethod": "directed"
            }
            }
            options["edges"]["length"] = 300
        return json.dumps(options, indent=4)


    #Takes the graph data and add the nodes and edges to a pyvis network
    def base_visualizer(self, graph_data):
        net = Network(height="600px", width="100%", notebook=False)
        print(graph_data)
        for node in graph_data["nodes"]:
            node_information = "\n".join(f"{key}: {value}" for key, value in node['properties'].items())
            print(node)
            net.add_node(label = node['properties']['name'], n_id = str(node['id']), group=node['labels'][0], title=node_information)
        i = 0
        for edge in graph_data["edges"]:
            edge_information = "\n".join(f"{key}: {value}" for key, value in edge['properties'].items())
            print(edge)
            net.add_edge(source=edge['source'], to =edge['target'], label=self.get_edge_label(graph_data['query_name'], edge, i), edge_data=edge['properties'], value=self.get_edge_weight(graph_data["query_name"], edge), title = edge_information)
            if (graph_data["query_name"] == "essential_track") or (graph_data["query_name"] == "artist_recommender") or ((graph_data["query_name"] == "track_recommender") and (edge['type'] == 'DISTANCE')) : i += 1
        net.set_options(self.node_display_options(graph_data["query_name"]))
        return net

    #Function for making the pyvis network and saving it into a static html file for displaying via Flask
    def create_network(self, graph_data):
        config = {"query": graph_data['query_name']}
        net = self.base_visualizer(graph_data)
        html = net.generate_html(f"{graph_data['query_name']}.html", notebook=False,)
        with open(fr"src\static\{graph_data['query_name']}_network.html", 'w') as file:
            file.write(html)
