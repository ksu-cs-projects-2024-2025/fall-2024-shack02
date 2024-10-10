from neo4j import GraphDatabase
import os

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=('neo4j', 'password'))

def create_graph_from_csv():
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///clean_graph_data.csv' AS row
    MERGE (t:Track {
        id: row.track_id, 
        name: row.track_name, 
        duration_ms: toInteger(row.duration_ms), 
        explicit: toBoolean(row.explicit), 
        track_number: toInteger(row.track_number)
    })
    MERGE (a:Artist {
        id: row.artist_id, 
        name: row.artist_name, 
        followers: toInteger(row.followers), 
        popularity: toInteger(row.popularity)
    })
    MERGE (b:Album {
        id: row.album_id, 
        name: row.album_name, 
        release_date: row.release_date
    })
    MERGE (a)-[:CREATED]->(t)
    MERGE (b)-[:INCLUDES]->(t);
    """
    with driver.session() as session:
        result = session.run(query)

    track_features = ["danceability","energy","tempo","valence","acousticness","instrumentalness","liveness","speechiness","key","mode","loudness","time_signature"]
    for f in track_features:
        create_track_feature_relationships(f)

    return




def fetch_graph_data(node_lim):
    query = f"""
    MATCH (a:Artist)-[r:CREATED]->(t:Track)<-[v:INCLUDES]-(b:Album)
    RETURN a, t, b
    LIMIT {node_lim};
    """

    with driver.session() as session:
        result = session.run(query)

        network_data = [] 

     
        for record in result:
            artist_node = record["a"]  
            track_node = record["t"]   
            album_node = record["b"]   

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


def create_track_feature_relationships(feature):
    create_track_feature_node_query = f"""
    MERGE (tf:TrackFeature {{name: '{feature}'}})
    """

    query = f"""
    LOAD CSV WITH HEADERS FROM 'file:///clean_graph_data.csv' AS row
    WITH row
    WHERE row.id IS NOT NULL AND row.{feature} IS NOT NULL
    MERGE (f1:TrackFeature {{name: '{feature}'}})
    MERGE (t:Track {{id: row.track_id}})
    MERGE (t)-[r1:HAS_FEATURE]->(f1)
    SET r1.weight = row.{feature};
    """

    with driver.session() as session:
        result = session.run(create_track_feature_node_query)
        result = session.run(query)
    return

