from neo4j import GraphDatabase
import os

class Neo4jQueryEngine:
    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.driver = GraphDatabase.driver(self.uri, auth=('neo4j', 'password'))
        self.track_features = ["danceability","energy","tempo","valence","acousticness","instrumentalness","liveness","speechiness","key","mode","loudness","time_signature"]


    #Sets up the track feature relationships between individual tracks and the respective track feature nodes
    def create_track_feature_relationships(self, feature):
        create_track_feature_node_query = f"""
        MERGE (tf:TrackFeature {{name: '{feature}'}})
        """

        query = f"""
        LOAD CSV WITH HEADERS FROM 'file:///graph_data.csv' AS row
        WITH row
        MERGE (f1:TrackFeature {{name: '{feature}'}})
        MERGE (t:Track {{id: row.track_id}})
        MERGE (t)-[r1:HAS_FEATURE]->(f1)
        SET r1.weight = row.{feature};
        """

        with self.driver.session() as session:
            result = session.run(create_track_feature_node_query)
            result = session.run(query)
        return  

    #Loads the graph_data csv into the neo4j dbms, setting up the initial track, artist, and feature nodes
    def create_graph_from_csv(self):
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///graph_data.csv' AS row
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
        with self.driver.session() as session:
            result = session.run(query)

        for f in self.track_features:
            self.create_track_feature_relationships(f)

        return

    #parses a query result into graph components that can be displayed with pyvis
    def parse_query_results(self, result, config):
        network_data = []
        for record in result:
            record_dict = {}
            if config['artists']:
                artist_node = record["a"]  
                record_dict['artist'] = {
                        "id": artist_node["id"],
                        "name": artist_node["name"],
                        "followers": artist_node["followers"],
                        "popularity": artist_node["popularity"]
                    }
            if config['tracks']:
                track_node = record["t"]
                record_dict['track'] = {
                        "id": track_node["id"],
                        "name": track_node["name"],
                        "duration_ms": track_node["duration_ms"],
                        "explicit": track_node["explicit"],
                        "track_number": track_node["track_number"]
                    }
            if config['albums']:
                album_node = record["b"]
                record_dict['album'] = {
                        "id": album_node["id"],
                        "name": album_node["name"],
                        "release_date": album_node["release_date"]
                    }
            if config['track_features']:
                track_feature_node = record["f"]
                record_dict['track_features'] = {
                        "name": track_feature_node["name"]
                    }
            if config['genres']:
                genre_node = record["g"]
                record_dict['genre'] = {
                        "name": genre_node["name"]
                    }
            network_data.append(record_dict)
        return network_data

    #Helper function for making queries and parsing them 
    def query_database(self, query, config):
        with self.driver.session() as session:
            result = session.run(query)
            if config['graph_data']:
                network_data =self.parse_query_results(result, config)
                return network_data
            else:
                return [record["name"] for record in result]

    #Generic graph query to display data
    def fetch_graph_data(self, node_lim):
        query = f"""
        MATCH (a:Artist)-[r:CREATED]->(t:Track)<-[v:INCLUDES]-(b:Album)
        RETURN a, t, b
        LIMIT {node_lim};
        """
        config = {
            'tracks': True,
            'artists': True,
            'albums': True,
            'track_features':False,
            'genres': False,
            'graph_data': True
        }

        return self.query_database(query, config)



    #Customizable graph query for the home page
    def home_graph(self, artist, tracks, albums, track_features, genres, node_lim):
        query = f"""
        MATCH (a:Artist {{name: '{artist}'}})
        RETURN a
        LIMIT {node_lim}
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            network_data = self.parse_query_results(result, artist=True, tracks=tracks, albums=albums, genres=genres)   

        return


    #Artist essential track query 
    def essential_track(self, artist, node_lim):
        query = f"""
        MATCH (a:Artist {{name: '{artist}'}})-[r:CREATED]->(t:Track)-[r1:HAS_FEATURE]->(f:TrackFeature)
        RETURN a, t, f
        LIMIT {node_lim}
        """

        config = {
            'tracks': True,
            'artists': True,
            'albums': False,
            'track_features':True,
            'genres': False,
            'graph_data': True
        }

        return self.query_database(query, config)

    def get_artists(self):
        query = f"""
        MATCH (a:Artist) RETURN a.name as name
        """

        with self.driver.session() as session:
            result = session.run(query)
            artists = [record["name"] for record in result]
        return artists

    def get_track_features(self):
        query = f"""
        MATCH (f:TrackFeature) RETURN f.name as name
        """

        with self.driver.session() as session:
            result = session.run(query)
            features = [record["name"] for record in result]
        return features

    #Other querie pages
    # def 