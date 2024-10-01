from neo4j import GraphDatabase
import os

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

network_data = fetch_graph_data()
print(network_data)