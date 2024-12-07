from neo4j import GraphDatabase
import neo4j
import os
from math import sqrt

#This class acts as the model, containing the logic for setting up the database and the queries for accessing the database and parsing the data from the database so it can be useable with pyvis.
class Neo4jQueryEngine:
    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.driver = GraphDatabase.driver(self.uri, auth=('neo4j', 'password'))
        self.track_features = ["danceability","energy","tempo","valence","acousticness","instrumentalness","liveness","speechiness","loudness"]
        self.track_structure = ["key","mode","time_signature"]
        load_data = input("Enter y to load data, only necessary on 1st load. Make sure graph_data.csv is located in neo4j database. Load time is slightly long: ")
        if load_data.lower() == "y": self.create_graph_from_csv()


    #Sets up the track feature relationships between individual tracks and the respective track feature nodes
    def create_track_feature_relationships(self):
        query = """
        LOAD CSV WITH HEADERS FROM 'file:///graph_data.csv' AS row
        WITH row
        LIMIT 10000
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
        LIMIT 10000
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
        LIMIT 10000
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
        SET g.id = toString(id(g))
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
    

    #generalized parse query results function, taking a query apart into nodes and edges and returning a graph data dictionary that contains these nodes and edges and a note of what query was made
    def parse_query_results(self, result, query):
        graph_data = {
            'query_name': query,
            'nodes': [],
            'edges': []
        }

        node_set = set()
        edge_set = set()
        for record in result:
            for key, value in record.items():
                if isinstance(value, neo4j.graph.Node):
                    node_id = value.element_id
                    if node_id not in node_set:
                        graph_data['nodes'].append({
                            "id": node_id,
                            "labels": list(value.labels),
                            "properties": dict(value)
                        })
                        node_set.add(node_id)
                if isinstance(value, neo4j.graph.Relationship):
                    edge_id = value.id
                    if edge_id not in edge_set:
                        graph_data['edges'].append({
                            "id": edge_id,
                            "type": value.type,
                            "source": value.start_node.element_id,
                            "target": value.end_node.element_id,
                            "properties": dict(value)
                        })
                        edge_set.add(edge_id)
        return graph_data


    def query_database(self, query, config, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters=parameters)
            if config:
                network_data =self.parse_query_results(result, query=config["query_type"])
                return network_data
            else:
                return [record["name"] for record in result]

    #Generic graph query to display data
    def fetch_graph_data(self, node_lim):
        query = f"""
        MATCH (a:Artist)-[r:CREATED]->(t:Track)<-[v:INCLUDES]-(b:Album)
        RETURN a, t, b, r, v
        LIMIT {node_lim};
        """
        config = {
            'node_labels': ['a','b','t'],
            'edge_labels': ['r','v'],
            'query_type': "home_query"
        }

        return self.query_database(query, config)

    #TODO: If time, make a query displaying the data model in the graph
    def home_graph(self, artist):
        query = """
        MATCH (a:Artist {name: $artist})-[c:CREATED]->(t:Track)<-[i:INCLUDES]-(al:Album),
        (t)-[hf:HAS_FEATURE]->(f:TrackFeature),
        (t)-[hs:HAS_STRUCTURE]->(s:TrackStructure),
        (t)-[bt:BELONGS_TO]->(g:Genre)
        WITH a, f, s, g, c, i, hf, hs, bt, al, t
        LIMIT 10
        RETURN a, f, s, t, al, g, c, i, hf, hs, bt
        """
        config = {
            "query_type": "home"
        }
        parameters = {
            "artist": artist
        }

        return self.query_database(query, config, parameters)
    
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
        WITH t, a, f.name as feature_name, r1.weight as weight, $centroid AS centroid, r
        WITH t, a, centroid, collect(feature_name) AS features, collect(weight) AS weights, r
        WHERE size(features) > 0
        WITH t, a, centroid, r,
            reduce(s = 0.0, i IN range(0, size(features) - 1) | 
                s + toFloat(weights[i] - centroid[features[i]])^2) AS squared_distance_sum
        WITH t, a, sqrt(squared_distance_sum) AS distance, r
        SET r.distance = distance
        RETURN a, t, r
        ORDER BY r.distance ASC
        LIMIT 10
        """

        config = {
            'node_labels': ['a','t'],
            'edge_labels': ['r'],
            'query_type': "essential_track"
        }

        parameters = {
            'artist': artist,
            'centroid': centroid
        }

        return self.query_database(query, config, parameters=parameters)

    def shortest_path(self, artist_1, artist_2):
        query =  """
        MATCH (p1:Artist {name: $artist_1})
        MATCH (p2:Artist {name: $artist_2})
        WITH p1, p2
        CALL apoc.algo.dijkstra(
        p1, 
        p2, 
        ':CREATED|FEATURES',
        'weight',
        1.0
        ) YIELD path, weight
        UNWIND nodes(path) AS node
        UNWIND relationships(path) as edge
        RETURN node, edge
        """
        config = {
            'query_type': "shortest_path"
        }

        parameters = {
            'artist_1': artist_1,
            'artist_2': artist_2
        }

        return self.query_database(query, config, parameters=parameters)

    def genre_overlap(self, genre_1, genre_2):
        query="""
        MATCH (g1:Genre {name: $genre_1}), (g2:Genre {name: $genre_2})
        MATCH (t:Track)-[r:BELONGS_TO]->(g1)
        MATCH (t)-[r1:BELONGS_TO]->(g2)
        WITH t, g1, g2, r1, r
        LIMIT 15
        RETURN t, g1, g2, r1, r
        """

        config = {
            'node_labels': ['t','g1', 'g2'],
            'edge_labels': ['r1', 'r'],
            'query_type': "genre_overlap"
        }

        parameters = {
            'genre_1': genre_1,
            'genre_2': genre_2
        }

        return self.query_database(query, config, parameters=parameters)

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


    #TODO: Fix this query to use new query engine and in general
    def find_track_recommendations(self, track, artist, track_features, track_structures):
        track_feature_values = self.get_track_feature_values(track, artist)
        track_structure_values = self.get_track_structure_values(track, artist)
        query = """
        MATCH (f:TrackFeature)<-[r:HAS_FEATURE]-(t:Track)
        WHERE f.name IN $track_features and t.name <> $track
        MATCH (s:TrackStructure)<-[r2:HAS_STRUCTURE]-(t)
        WHERE s.name IN $track_structures AND r2.value = $track_structure_values[s.name]
        WITH t, sum((r.weight - $track_feature_values[f.name])^2) AS squared_distance_sum
        MATCH (input:Track {name: $track})<-[:CREATED]-(a:Artist {name: $artist})
        WITH input, t, sqrt(squared_distance_sum) AS distance
        ORDER BY distance ASC
        LIMIT 10
        MATCH (t)<-[c:CREATED]-(creator:Artist)
        CALL {
            WITH input, t, distance
            MERGE (input)-[rel:DISTANCE]->(t)
            ON CREATE SET rel.distance = distance
            ON MATCH SET rel.distance = distance
            RETURN rel
        }
        RETURN input, t, rel, creator, c
        """
        config = {
            'query_type': 'track_recommender'
        }
        parameters = {
            "track": track,
            "artist": artist,
            "track_features": track_features,
            "track_feature_values": track_feature_values,
            "track_structures": track_structures,
            "track_structure_values": track_structure_values,
        }

        return self.query_database(query, config, parameters)

        
    def compare_artist_centroids(self, main_artist_centroid, compared_artist_centroid):
        keys = set(main_artist_centroid.keys()).intersection(set(compared_artist_centroid.keys()))
        if not keys:
            return float('inf')
        distance = sqrt(sum((main_artist_centroid[key] - compared_artist_centroid[key]) ** 2 for key in keys))
        return distance


    def find_artist_recommendations(self, artist):
        main_artist_centroid = self.calculate_artist_centroid(artist)
        query = """
        MATCH (a:Artist)
        WHERE a.name <> $artist
        RETURN a.name as name
        """
        with self.driver.session() as session:
            result = session.run(query, artist=artist)
            artist_names = [record["name"] for record in result]

        artist_similarities = []
        for name in artist_names:
            compared_artist_centroid =self.calculate_artist_centroid(name)
            similarity_score = self.compare_artist_centroids(main_artist_centroid, compared_artist_centroid)
            artist_similarities.append((name, similarity_score))

        top_artists = sorted(artist_similarities, key=lambda x: x[1])[:10]
        
        top_artist_names = [artist[0] for artist in top_artists]
        distances = [artist[1] for artist in top_artists]
        artist_data = [{"name": name, "distance": dist} for name, dist in zip(top_artist_names, distances)]

        query = """
        UNWIND $artist_data AS artist_item
        MATCH (main:Artist {name: $main_artist}), (a:Artist {name: artist_item.name})
        MERGE (main)-[d:DISTANCE]->(a)
        ON CREATE SET d.distance = artist_item.distance
        ON MATCH SET d.distance = artist_item.distance
        WITH a, main, d, d.distance as distance
        ORDER by distance ASC
        RETURN a, main, d
        """

        config = {
            "query_type": "artist_recommender"
        }

        parameters = {
            'main_artist': artist,
            'artist_data': artist_data
        }
        
        return self.query_database(query,config,parameters)


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
