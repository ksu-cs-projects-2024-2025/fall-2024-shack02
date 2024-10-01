from flask import Flask, render_template
from pyvis.network import Network
from neo4j import GraphDatabase
import os

app = Flask(__name__)
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=('neo4j', 'password'))


def fetch_graph_data():
    query = """
    MATCH (a:Artist)-[r:CREATED]->(t:Track)<-[v:INCLUDES]-(b:Album)
    RETURN a, t, b
    LIMIT 25;
    """

    with driver.session() as session:
        result = session.run(query)

        network_data = []  # This will hold the nodes and relationships

        # Iterate over the results and extract data
        for record in result:
            artist_node = record["a"]  # Artist node
            track_node = record["t"]   # Track node
            album_node = record["b"]   # Album node

            # Collect nodes and their relationships
            network_data.append({
                "artist": {
                    "id": artist_node["id"],
                    "name": artist_node["name"],
                    "followers": artist_node["followers"],
                    "popularity": artist_node["popularity"]
                },
                "track": {
                    "id": track_node["id"],
                    "name": track_node["name"],
                    "duration_ms": track_node["duration_ms"],
                    "explicit": track_node["explicit"],
                    "track_number": track_node["track_number"]
                },
                "album": {
                    "id": album_node["id"],
                    "name": album_node["name"],
                    "release_date": album_node["release_date"]
                }
            })

        return network_data

#Creates a network from the neo4j backend, displaying the base network on the homepage. 
def create_network():
    # Initialize PyVis network
    net = Network(height="750px", width="100%", notebook=False)
    graph_data = fetch_graph_data()
    # Add nodes and edges to the network
    for data in graph_data:
        artist = data["artist"]
        track = data["track"]
        album = data["album"]

        # Add artist node
        net.add_node(artist["id"], label=artist["name"], title=f'Popularity: {artist["popularity"]}', group='artist')

        # Add track node
        net.add_node(track["id"], label=track["name"], title=f'Track number: {track["track_number"]}', group='track')

        # Add album node
        net.add_node(album["id"], label=album["name"], title=f'Release date: {album["release_date"]}', group='album')

        # Add edges between artist, track, and album
        net.add_edge(artist["id"], track["id"], label='CREATED')
        net.add_edge(album["id"], track["id"], label='INCLUDES')

    # Set options for better visualization
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


    net.generate_html(r"C:\Projects\fall-2024-shack02\src\static\network.html",notebook=False)


@app.route('/')
def index():
    create_network()
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)