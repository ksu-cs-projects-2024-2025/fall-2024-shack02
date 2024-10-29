from flask import Flask, render_template
from pyvis.network import Network
from neo4j import GraphDatabase
from neo4j_query_library import Neo4jQueryEngine
import os


class GraphVisualizer:
    def __init__(self):
        return

    def base_visualizer(self, graph_data, artist=False, track=False, album=False, genre=False, track_features=False):
        net = Network(height="600px", width="100%", notebook=False)
        for data in graph_data:
            print(data)
            if artist:
                artist_data = data["artist"]
                net.add_node(artist_data["id"], label=artist_data["name"], title=f'Popularity: {artist_data["popularity"]}', group='artist')
            if track:
                track_data = data["track"]       
                net.add_node(track_data["id"], label=track_data["name"], title=f'Track number: {track_data["track_number"]}', group='track', physics=False)
            if album:
                album_data = data["album"]
                net.add_node(album_data["id"], label=album_data["name"], title=f'Release date: {album_data["release_date"]}', group='album', physics=False)
            if genre:
                genre_data = data["genre"]
            if track_features:
                track_feature_data = data["track_features"]
            if artist and track:
                net.add_edge(artist_data["id"], track_data["id"], label='CREATED')
            if album and track:
                net.add_edge(album_data["id"], track_data["id"], label='INCLUDES')
            if track and track_features:
                print(track_feature_data, track_data)
                net.add_edge(track_feature_data["name"], track_data["id"], label="HAS_FEATURE", weight='weight')

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
            }
            }
        """)
        return net


    #Creates a network from the neo4j database
    def create_home_network(self, graph_data):
        net = self.base_visualizer(graph_data, artist=True, track=True, album=True)
        html = net.generate_html("home_network.html",notebook=False)
        with open(r"src\static\home_network.html", 'w') as file:
            file.write(html)


    def create_essential_network(self, graph_data):
        net = self.base_visualizer(graph_data, artist=True, track=True, track_features=True)
        html = net.generate_html("essential_song.html",notebook=False)
        with open(r"src\static\essential_song_network.html", 'w') as file:
            file.write(html)
