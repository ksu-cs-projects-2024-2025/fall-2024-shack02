from neo4j import GraphDatabase
import neo4j
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
    def parse_query_results_v2(self, result, query):
        graph_data = {
            'query_name': query,
            'nodes': [],
            'edges': []
        }

        node_set = set()
        edge_set = set()
        print("Parse Query Results V2")
        for record in result:
            for key, value in record.items():
                print(key,value)
                if isinstance(value, neo4j.graph.Node):
                    node_id = value.element_id
                    print(node_id,value)
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
        print("GRAPH DATA AFTER parse query results v2")
        print(graph_data)
        return graph_data


    def query_database_v2(self, query, config, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters=parameters)
            if config:
                network_data =self.parse_query_results_v2(result, query=config["query_type"])
                print("******In Query Database V2******")
                print(network_data)
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

        return self.query_database_v2(query, config)

    #TODO: If time, make a query displaying the data model in the graph
    # def home_graph(self, artist, tracks, albums, track_features, genres, node_lim):
    #     query = """
    #     MATCH (a:Artist {name: $artist})
    #     RETURN a
    #     LIMIT $node_lim
    #     """
        
    #     with self.driver.session() as session:
    #         result = session.run(query, artist=artist, node_lim=node_lim)
    #         network_data = self.parse_query_results(result, artist=True, tracks=tracks, albums=albums, genres=genres)   

    #     return network_data
    
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

        return self.query_database_v2(query, config, parameters=parameters)

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

        return self.query_database_v2(query, config, parameters=parameters)

    def genre_overlap(self, genre_1, genre_2):
        query="""
        MATCH (g1:Genre {name: $genre_1}), (g2:Genre {name: $genre_2})
        MATCH (t:Track)-[r:BELONGS_TO]->(g1)
        MATCH (t)-[r1:BELONGS_TO]->(g2)
        WITH t, g1, g2, r1, r
        LIMIT 25
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

        return self.query_database_v2(query, config, parameters=parameters)

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

        
        



    #TODO: Finish this query using new parsing engine
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
