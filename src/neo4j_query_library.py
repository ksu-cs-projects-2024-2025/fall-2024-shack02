from neo4j import GraphDatabase
import os

class Neo4jQueryEngine:
    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.driver = GraphDatabase.driver(self.uri, auth=('neo4j', 'password'))
        self.track_features = ["danceability","energy","tempo","valence","acousticness","instrumentalness","liveness","speechiness","loudness"]
        self.track_structure = ["key","mode","time_signature"]
        # self.create_graph_from_csv()


    #Sets up the track feature relationships between individual tracks and the respective track feature nodes
    def create_track_feature_relationships(self):
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///graph_data.csv' AS row
        WITH row
        LIMIT 1000
        UNWIND $features AS feature
        MERGE (f:TrackFeature {
        name: feature
        })
        WITH row, feature, f
        MERGE (t:Track {id: row.track_id})
        MERGE (t)-[r:HAS_FEATURE]->(f)
        SET r.weight = toFloat(row[feature])
        """
        with self.driver.session() as session:
            session.run(query, features=self.track_features)
        return  
    
    def create_track_structure_relationships(self):
        query ="""
        LOAD CSV WITH HEADERS FROM 'file:///graph_data.csv' AS row
        WITH row
        LIMIT 1000
        UNWIND $structures AS structure
        MERGE (s:TrackStructure {name: structure})
        WITH row, structure, s
        MERGE (t:Track {id: row.track_id})
        MERGE (t)-[r:HAS_STRUCTURE]->(s)
        SET r.value = toFloat(row[structure])
        """
        with self.driver.session() as session:
            session.run(query, structures=self.track_structure)
        return  

    #Loads the graph_data csv into the neo4j dbms, setting up the initial track, artist, and feature nodes
    def create_graph_from_csv(self):
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///graph_data.csv' AS row
        WITH row
        LIMIT 1000
        MERGE (t:Track {
            id: row.track_id, 
            name: row.track_name, 
            duration_ms: toInteger(row.duration_ms), 
            explicit: toBoolean(row.explicit), 
            track_number: toInteger(row.track_number),
            artist_feature: row.featured_artists
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
        MERGE (b)-[:INCLUDES]->(t)
        WITH row, t
        , CASE WHEN row.genres CONTAINS ',' THEN SPLIT(row.genres, ',')
            ELSE [row.genres]
        END AS genre_list
        UNWIND genre_list AS genre
        WITH t, genre
        WHERE genre IS NOT NULL AND genre <> ''
        MERGE (g:Genre {name: genre})
        MERGE (t)-[:BELONGS_TO]->(g);
        """
        artist_features_query = """
        MATCH (t:Track)
        WHERE t.artist_feature IS NOT NULL
        WITH t
        MATCH (a:Artist)
        WHERE t.artist_feature = a.name
        MERGE (t)-[:FEATURES]->(a);
        """
        with self.driver.session() as session:
            result = session.run(query)
            result = session.run(artist_features_query)

        self.create_track_feature_relationships()
        self.create_track_structure_relationships()
        return

    #parses a query result into graph components that can be displayed with pyvis
    def parse_query_results(self, result, config):
        network_data = []
        for i,record  in enumerate(result):
            print(f"RECORD {i}")
            print(i,record)
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
                if config['query'] == "essential_track":
                    record_dict['track']['distance'] = record["distance"]
                    record_dict['track']['rank'] = i + 1
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
                        "id": track_feature_node["element_id"],
                        "name": track_feature_node["name"],
                        "weight": record["r1.weight"]
                    }
            if config['genres']:
                genre_node = record.get("g1")
                if genre_node == None:
                    genre_node = record.get("g2")
                record_dict['genre'] = {
                        "name": genre_node["name"]
                    }
            print(f"RECORD_DICT {i}")
            print(record_dict)
            network_data.append(record_dict)

        # print(network_data)
        return network_data
    
    def parse_path_query(self, result, config):
        network_data = []
        for i,record in enumerate(result):
            print(f"Record {i}")
            # print(record)    
            record_dict = {}
            record_dict['nodes'] = []
            for node in record['nodes']:
                node_dict = {}
                node_dict["id"] = node["id"]
                node_dict["type"] = list(node.labels)[0]
                node_dict["name"] = node["name"]
                record_dict['nodes'].append(node_dict)
                print(node_dict)
            record_dict['edges'] = []
            for i,edge in enumerate(record['edges']):
                print(f"edge {i}")
                # print(edge)
                edge_dict = {}
                edge_dict["node_1"] = edge.nodes[0]["id"]
                edge_dict["node_2"] = edge.nodes[1]["id"]
                edge_dict["type"] = edge.type
                print(edge_dict)
                record_dict['edges'].append(edge_dict)
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
            'graph_data': True,
            "query" :"na"
        }

        return self.query_database(query, config)



    #Customizable graph query for the home page
    def home_graph(self, artist, tracks, albums, track_features, genres, node_lim):
        query = """
        MATCH (a:Artist {name: $artist})
        RETURN a
        LIMIT $node_lim
        """
        
        with self.driver.session() as session:
            result = session.run(query, artist=artist, node_lim=node_lim)
            network_data = self.parse_query_results(result, artist=True, tracks=tracks, albums=albums, genres=genres)   

        return network_data
    
    def calculate_artist_centroid(self, artist):
        query = """
        MATCH (a:Artist {name: $artist})-[r:CREATED]->(t:Track)-[r1:HAS_FEATURE]->(f:TrackFeature)
        WITH f.name as feature_name, avg(r1.weight) as centroid_weight
        RETURN feature_name, centroid_weight
        """

        with self.driver.session() as session:
            result = session.run(query, artist=artist)
            list_records = result.data()

        centroid = {record['feature_name']: record['centroid_weight'] for record in list_records}
        return centroid
    
    def essential_track(self, artist):
        centroid = self.calculate_artist_centroid(artist)
        query = """
        MATCH (a:Artist {name: $artist})-[r:CREATED]->(t:Track)
        WHERE EXISTS { MATCH (t)-[:HAS_FEATURE]->(:TrackFeature) }
        MATCH (t)-[r1:HAS_FEATURE]->(f:TrackFeature)
        WITH t, a, f.name as feature_name, r1.weight as weight, $centroid AS centroid
        WITH t, a, centroid, collect(feature_name) AS features, collect(weight) AS weights
        WHERE size(features) > 0
        WITH t, a, centroid, 
            reduce(s = 0.0, i IN range(0, size(features) - 1) | 
                s + toFloat(weights[i] - centroid[features[i]])^2) AS squared_distance_sum
        WITH t, a, sqrt(squared_distance_sum) AS distance
        ORDER BY distance ASC
        RETURN a, t, distance
        LIMIT 10
        """

        config = {
            'tracks': True,
            'artists': True,
            'albums': False,
            'track_features':False,
            'genres': False,
            'graph_data': True,
            "query": "essential_track"
        }

        with self.driver.session() as session:
            result = session.run(query, centroid=centroid, artist=artist)
            result = result.to_eager_result()
            print(result.records)
        return self.parse_query_results(result.records, config)

    def shortest_path(self, artist_1, artist_2):
        query = """
        MATCH (p1:Artist {name: $artist_1})  MATCH (p2:Artist {name: $artist_2}),
        p = shortestPath((p1)-[:CREATED|FEATURES*..10]-(p2))
        WITH p
        WHERE length(p) > 1
        RETURN nodes(p) as nodes, relationships(p) as edges
        """

        config = {
            'tracks': True,
            'artists': True,
            'albums': False,
            'track_features':False,
            'genres': False,
            'graph_data': True,
            "query": "shortest_path"
        }

        with self.driver.session() as session:
            result = session.run(query, artist_1=artist_1, artist_2=artist_2)
            result = result.to_eager_result()
        return self.parse_path_query(result.records, config)

    def genre_overlap(self, genre_1, genre_2):
        query="""
        MATCH (g1:Genre {name: $genre_1}), (g2:Genre {name: $genre_2})
        MATCH (t:Track)-[r:BELONGS_TO]->(g1)
        MATCH (t)-[r1:BELONGS_TO]->(g2)
        WITH t, g1, g2
        LIMIT 25
        RETURN t, g1, g2
        """

        config = {
            'tracks': True,
            'artists': False,
            'albums': False,
            'track_features':False,
            'genres': True,
            'graph_data': True,
            "query": "genre_overlap"
        }

        with self.driver.session() as session:
            result = session.run(query, genre_1=genre_1, genre_2=genre_2)
            result = result.to_eager_result()
        return self.parse_query_results(result.records, config)

    def get_track_feature_values(self, track, artist):
        query ="""
        MATCH (a:Artist {name: $artist})-[:CREATED]->(t:Track {name: $track})-[r1:HAS_FEATURE]->(f:TrackFeature)
        WITH f.name as feature_name, r1.weight as feature_weight
        RETURN feature_name,feature_weight
        """
        with self.driver.session() as session:
            result = session.run(query, artist=artist, track=track)
            list_records = result.data()

        track_feature_values = {record['feature_name']: record['feature_weight'] for record in list_records}
        return track_feature_values

    def get_track_structure_values(self,track,artist):
        query ="""
        MATCH (a:Artist {name: $artist})-[:CREATED]->(t:Track {name: $track})-[r1:HAS_STRUCTURE]->(s:TrackStructure)
        WITH s.name as structure_name, r1.value as structure_value
        RETURN structure_name,structure_value
        """
        with self.driver.session() as session:
            result = session.run(query, artist=artist, track=track)
            list_records = result.data()

        track_structure_values = {record['structure_name']: record['structure_value'] for record in list_records}
        return track_structure_values


    def find_track_recommendations(self, track, artist, genre, track_features, track_structures):
        track_feature_values = self.get_track_feature_values(track, artist)
        track_structure_values = self.get_track_structure_values(track, artist)
        query = """
        MATCH (f:TrackFeature)<-[r:HAS_FEATURE]-(t:Track)-[:BELONGS_TO]->(g:Genre {name: $genre})
        WHERE f.name in $track_features
        MATCH (s:TrackStructure)<-[r2:HAS_STRUCTURE]-(t)
        WHERE s.name in $track_structures and r2.value = $track_structure_values[s.name]
        WITH f.name as feature_name, r.weight as weight, t, g, $track_feature_values as original_track_features
        WITH t, g, sum((original_track_features[feature_name] - weight)^2) as squared_distance_sum
        WITH t, g, sqrt(squared_distance_sum) as distance
        ORDER by distance ASC
        RETURN t, g, distance
        LIMIT 10
        """
        config = {
            'tracks': True,
            'artists': False,
            'albums': False,
            'track_features':False,
            'genres': True,
            'graph_data': True,
            "query": "track_recommendations"
        }
        with self.driver.session() as session:
            result = session.run(query, track_features = track_features,
                                        track_feature_values = track_feature_values,
                                        track_structures= track_structures,
                                        track_structure_values = track_structure_values,
                                        genre=genre
            )
            result = result.to_eager_result()
            print("RESULTS OF TRACK RECOMMENDATION")
            print(result)
        return self.parse_query_results(result.records, config)

    def calculate_artist_centroids(self, artists):
        query = """
        UNWIND $artists AS artist_name
        MATCH (a:Artist {name: artist_name})-[r:CREATED]->(t:Track)-[r1:HAS_FEATURE]->(f:TrackFeature)
        WITH artist_name, f.name as feature_name, avg(r1.weight) as centroid_weight
        RETURN artist_name, collect({feature_name, centroid_weight}) as centroid data
        """

        with self.driver.session() as session:
            result = session.run(query, artist=artist)
            list_records = result.data()

        centroid = {record['feature_name']: record['centroid_weight'] for record in list_records}
        return centroid



    def get_genre_artist_centroids(self, genre):
        query ="""
        MATCH (a:Artist)-[:CREATED]->(t:Track)-[:BELONGS_TO]->(g:Genre {name: 'acoustic pop'})
        RETURN DISTINCT a.name AS artist_name
        """
        with self.driver.session() as session:
            result = session.run(query, genre=genre)
            artists = result.data()

        
        




    def find_artist_recommendations(self, artist, genre):
        genre_artist_centroids = self.get_genre_artist_centroids(genre)
        artist_centroid = self.calculate_artist_centroid(artist)
        query = """
        MATCH (a:Artist
        """


        config = {
            'tracks': False,
            'artists': True,
            'albums': False,
            'track_features':False,
            'genres': True,
            'graph_data': True,
            "query": "artist_recommendations"
        }



    def get_named_values(self, data):
        query = f"""
        MATCH (d:{data}) WITH d.name as name ORDER BY name ASC RETURN name
        """

        with self.driver.session() as session:
            result = session.run(query,data =data)
            list_of_data = [record["name"] for record in result]
        return list_of_data

    def get_track_features(self):
        query = """
        MATCH (f:TrackFeature) RETURN f.name as name
        """

        with self.driver.session() as session:
            result = session.run(query)
            features = [record["name"] for record in result]
        return features

    def get_tracks_for_artist(self, artist):
        query = """
        MATCH (a:Artist {name: $artist})-[:CREATED]->(t:Track) RETURN t.name as name
        """

        with self.driver.session() as session:
            result = session.run(query,artist=artist)
            features = [record["name"] for record in result]
        return features

    #Other querie pages
    # def 