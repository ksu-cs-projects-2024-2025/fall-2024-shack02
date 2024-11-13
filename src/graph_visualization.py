from flask import Flask, render_template
from pyvis.network import Network
from neo4j import GraphDatabase
from neo4j_query_library import Neo4jQueryEngine
import os


class GraphVisualizer:
    def __init__(self):
        return

    def base_visualizer(self, graph_data, config, artist=False, track=False, album=False, genre=False, track_features=False):
        net = Network(height="600px", width="100%", notebook=False)
        for data in graph_data:
            if 'artist' in data and artist:
                artist_data = data["artist"]
                net.add_node(artist_data["id"], label=artist_data["name"], title=f'Popularity: {artist_data["popularity"]}', group='Artist', physics=False)
            if track:
                track_data = data["track"]       
                net.add_node(track_data["id"], label=track_data["name"], title=f'Track number: {track_data["track_number"]}', group='Track', physics=False)
            if album:
                album_data = data["album"]
                net.add_node(album_data["id"], label=album_data["name"], title=f'Release date: {album_data["release_date"]}', group='Album', physics=False)
            if genre:
                genre_data = data["genre"]
                net.add_node(genre_data["name"], label=genre_data["name"], title=genre_data["name"], group = 'Genre', physics=False)
            if track_features:
                track_feature_data = data["track_features"]
                net.add_node(track_feature_data["name"], label=track_feature_data["name"],title=f'{track_feature_data["name"]}',group='TrackFeature', physics=False)
            if artist and track:
                if config["query"] == "essential_track":
                    if track_data['distance'] != 0:
                        weight = 1 / track_data['distance']
                    else:
                        weight = 100
                    # weight = 1 / (1 - track_data['distance'])
                    net.add_edge(artist_data["id"], track_data["id"], label=f'Rank: {track_data['rank']}', title=f"Euclidean distance from artist centroid: {track_data["distance"]}", value=weight)
                    net.add_edge(artist_data["id"], track_data["id"], label='CREATED')
                else:
                    net.add_edge(artist_data["id"], track_data["id"], label="CREATED")
            if album and track:
                net.add_edge(album_data["id"], track_data["id"], label='INCLUDES')
            if track and track_features:
                net.add_edge(track_data["id"], track_feature_data["name"], label=track_feature_data["weight"], value=track_feature_data["weight"], title=round(track_feature_data["weight"], 3))
            if genre and track:
                net.add_edge(track_data["id"], genre_data["name"], label="BELONGS_TO")

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

    def path_visualizer(self, graph_data):
        net = Network(height="600px", width="100%", notebook=False)
        for graph_data in graph_data:
            print("PATH_GRAPH_DATA")
            print(graph_data)
            for node in graph_data['nodes']:
                net.add_node(label= node['name'],n_id = node['id'], group=node['type'])
            for edge in graph_data['edges']:
                net.add_edge(edge['node_1'], to=edge['node_2'], label=edge['type'])
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
        

    #Creates a network from the neo4j database
    def create_home_network(self, graph_data):
        config = {"query": "na"}
        net = self.base_visualizer(graph_data,config,artist=True, track=True, album=True)
        html = net.generate_html("home_network.html",notebook=False)
        with open(r"src\static\home_network.html", 'w') as file:
            file.write(html)


    def create_essential_network(self, graph_data):
        config = {"query": "essential_track"}
        print("GRAPH_DATA******")
        print(graph_data)
        net = self.base_visualizer(graph_data, config, artist=True, track=True)
        html = net.generate_html("essential_song.html",notebook=False)
        with open(r"src\static\essential_song_network.html", 'w') as file:
            file.write(html)

    def create_shortest_path_network(self, graph_data):
        config = {"query": "shortest_path"}
        net = self.path_visualizer(graph_data)
        html = net.generate_html("shortest_path.html",notebook=False)
        with open(r"src\static\shortest_path_network.html", 'w') as file:
            file.write(html)

    def create_genre_overlap_graph(self,graph_data):
        config = {"query": "genre_overlap"}
        net = self.base_visualizer(graph_data, config=config,genre=True, track=True)
        html = net.generate_html("genre_overlap.html", notebook=False)
        with open(r"src\static\genre_overlap_network.html", 'w') as file:
            file.write(html)