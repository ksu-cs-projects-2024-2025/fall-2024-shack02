import pytest
from unittest.mock import Mock
from flask import Flask
from routes.artist_recommender import create_blueprint as bp_ar
from routes.essential_song import create_essential_song_blueprint as bp_es
from routes.track_recommender import create_blueprint as bp_tr
from routes.shortest_path import create_blueprint as bp_sp
from routes.genre_overlap import create_blueprint as bp_go

#This file is for testing the Flask API and making sure that each response returns the correct info when it is given sample graph data.
@pytest.fixture
def test_client():
    mock_query = Mock()
    mock_visualizer = Mock()

    app = Flask(__name__, template_folder=r"C:\Projects\fall-2024-shack02\src\templates")
    print(app.jinja_env.list_templates())

    blueprint_ar = bp_ar(mock_query, mock_visualizer, 11)
    blueprint_es = bp_es(mock_query, mock_visualizer, 11)
    blueprint_tr = bp_tr(mock_query, mock_visualizer, 11)
    blueprint_sp = bp_sp(mock_query, mock_visualizer, 11)
    blueprint_go = bp_go(mock_query, mock_visualizer, 11)
    
    app.register_blueprint(blueprint_ar)
    app.register_blueprint(blueprint_es)
    app.register_blueprint(blueprint_tr)
    app.register_blueprint(blueprint_sp)
    app.register_blueprint(blueprint_go)

    with app.test_client() as client:
        yield client, mock_query, mock_visualizer

#Get Tests for artists recommendation page
def test_get_artist_recommender_page(test_client):
    client, mock_query, _ = test_client

    mock_query.get_named_values.return_value = ["Artist1", "Artist2", "Artist3"]

    response = client.get("/artist_recommender")
    assert response.status_code == 200
    assert b"Artist1" in response.data
    assert b"Artist2" in response.data
    assert b"Artist3" in response.data

#Post Tests for artists recommendation page
def test_post_artist_recommender(test_client):
    client, mock_query, mock_visualizer = test_client

    mock_query.get_named_values.return_value = ["Artist1", "Artist2", "Artist3", "Genre1", "Genre2"]
    mock_query.find_artist_recommendations.return_value = {
    "query_name": "artist_recommender",
    "nodes": [
        {"id": "A1", "labels": ["Artist"], "properties": {"followers": 5000, "popularity": 50, "name": "Artist1", "id": "001"}},
        {"id": "A2", "labels": ["Artist"], "properties": {"followers": 8000, "popularity": 60, "name": "Artist2", "id": "002"}},
        {"id": "A3", "labels": ["Artist"], "properties": {"followers": 12000, "popularity": 70, "name": "Artist3", "id": "003"}},
        {"id": "A4", "labels": ["Artist"], "properties": {"followers": 3000, "popularity": 40, "name": "Artist4", "id": "004"}},
        {"id": "A5", "labels": ["Artist"], "properties": {"followers": 10000, "popularity": 65, "name": "Artist5", "id": "005"}},
        {"id": "A6", "labels": ["Artist"], "properties": {"followers": 6000, "popularity": 50, "name": "Artist6", "id": "006"}},
        {"id": "A7", "labels": ["Artist"], "properties": {"followers": 7000, "popularity": 60, "name": "Artist7", "id": "007"}},
        {"id": "A8", "labels": ["Artist"], "properties": {"followers": 15000, "popularity": 70, "name": "Artist8", "id": "008"}},
        {"id": "A9", "labels": ["Artist"], "properties": {"followers": 4000, "popularity": 40, "name": "Artist9", "id": "009"}},
        {"id": "A10", "labels": ["Artist"], "properties": {"followers": 30000, "popularity": 65, "name": "Artist10", "id": "010"}},
        {"id": "A11", "labels": ["Artist"], "properties": {"followers": 20000, "popularity": 65, "name": "Artist11", "id": "011"}}
    ],
    "edges": [
        {"id": 0, "type": "DISTANCE", "source": "A1", "target": "A2", "properties": {"distance": 0.05}},
        {"id": 1, "type": "DISTANCE", "source": "A1", "target": "A3", "properties": {"distance": 0.08}},
        {"id": 2, "type": "DISTANCE", "source": "A1", "target": "A4", "properties": {"distance": 0.12}},
        {"id": 3, "type": "DISTANCE", "source": "A1", "target": "A5", "properties": {"distance": 0.07}},
        {"id": 4, "type": "DISTANCE", "source": "A1", "target": "A6", "properties": {"distance": 0.10}},
        {"id": 5, "type": "DISTANCE", "source": "A1", "target": "A7", "properties": {"distance": 0.5}},
        {"id": 6, "type": "DISTANCE", "source": "A1", "target": "A8", "properties": {"distance": 0.8}},
        {"id": 7, "type": "DISTANCE", "source": "A1", "target": "A9", "properties": {"distance": 0.2}},
        {"id": 8, "type": "DISTANCE", "source": "A1", "target": "A10", "properties": {"distance": 0.7}},
        {"id": 9, "type": "DISTANCE", "source": "A1", "target": "A11", "properties": {"distance": 0.11}}
    ]
    }

    response = client.post(
        "/artist_recommender",
        data={"artist_dropdown": "Artist1"},
    )

    assert response.status_code == 200
    assert b"Artist1" in response.data

    mock_query.find_artist_recommendations.assert_called_once_with("Artist1")
    mock_visualizer.create_network.assert_called_once_with(mock_query.find_artist_recommendations.return_value)


#Post Tests for essential track page
def test_post_essential_song(test_client):
    client, mock_query, mock_visualizer = test_client

    mock_query.get_named_values.return_value = ["Artist1", "Artist2", "Artist3"]
    mock_query.essential_track.return_value = {
    "query_name": "essential_track",
    "nodes": [
        {"id": "A1", "labels": ["Artist"], "properties": {"followers": 5000, "popularity": 50, "name": "Artist1", "id": "001"}},
        {"id": "T1", "labels": ["Track"], "properties": {'duration_ms': 225640, 'explicit': False, 'name': 'Track1', 'track_number': 11, 'id': 'T1', 'artist_feature': 'A2'}},
        {"id": "T2", "labels": ["Track"], "properties": {'duration_ms': 555555, 'explicit': True, 'name': 'Track2', 'track_number': 1, 'id': 'T2', 'artist_feature': 'A3'}},
        {"id": "T3", "labels": ["Track"], "properties": {'duration_ms': 333333, 'explicit': False, 'name': 'Track3', 'track_number': 9, 'id': 'T3', 'artist_feature': 'A4'}},
    ],
    "edges": [
        {"id": 1, "type": "CREATED", "source": "A1", "target": "T1", "properties": {"distance": 0.12}},
        {"id": 2, "type": "CREATED", "source": "A1", "target": "T2", "properties": {"distance": 0.05}},
        {"id": 3, "type": "CREATED", "source": "A1", "target": "T3", "properties": {"distance": 0.08}},
    ]
    }

    response = client.post("/essential_song", data={"artist_dropdown": "Artist1"},)
    
    assert response.status_code == 200
    assert b"Artist1" in response.data
    
    mock_query.essential_track.assert_called_once_with("Artist1")
    mock_visualizer.create_network.assert_called_once_with(mock_query.essential_track.return_value)


#Post Tests for track recommendation page
def test_post_track_recommender(test_client):
    client, mock_query, mock_visualizer = test_client

    mock_query.get_named_values.return_value = ["Artist1", "Artist2"]
    mock_query.track_features = ["Feature1", "Feature2"]
    mock_query.track_structure = ["Structure1", "Structure2"]
    mock_query.get_tracks_for_artist.return_value = ["Track1", "Track2"]
    mock_query.find_track_recommendations.return_value = {
    'query_name': 'track_recommender',
    'nodes': [
        {'id': 'T1', 'labels': ['Track'], 'properties': {'duration_ms': 300000, 'explicit': False, 'name': 'Track1', 'track_number': 1, 'id': 'T1', 'artist_feature': 'Artist1'}},
        {'id': 'T2', 'labels': ['Track'], 'properties': {'duration_ms': 200000, 'explicit': False, 'name': 'Track2', 'track_number': 2, 'id': 'T2', 'artist_feature': 'Artist2'}},
        {'id': 'A1', 'labels': ['Artist'], 'properties': {'followers': 1000, 'popularity': 50, 'name': 'Artist1', 'id': 'artist_001'}},
        {'id': 'T3', 'labels': ['Track'], 'properties': {'duration_ms': 250000, 'explicit': False, 'name': 'Track3', 'track_number': 3, 'id': 'T3', 'artist_feature': 'Artist3'}},
        {'id': 'A2', 'labels': ['Artist'], 'properties': {'followers': 5000, 'popularity': 75, 'name': 'Artist2', 'id': 'artist_002'}},
    ],
    'edges': [
        {'id': 1, 'type': 'DISTANCE', 'source': 'T1', 'target': 'T2', 'properties': {'distance': 0.1}},
        {'id': 2, 'type': 'CREATED', 'source': 'A1', 'target': 'T2', 'properties': {}},
        {'id': 3, 'type': 'DISTANCE', 'source': 'T1', 'target': 'T3', 'properties': {'distance': 0.2}},
        {'id': 4, 'type': 'CREATED', 'source': 'A2', 'target': 'T3', 'properties': {}},
    ]
    }

    response = client.post("/track_recommender", data={
            "artist_dropdown": "Artist1",
            "track_dropdown": "Track1",
            "track_features": ["Feature1"],
            "track_structures": ["Structure1"],
        })
    
    assert response.status_code == 200
    assert b"Artist1" in response.data
    assert b"Track1" in response.data
    assert b"Feature1" in response.data
    assert b"Structure1" in response.data
    
    mock_query.get_tracks_for_artist.assert_called_once_with("Artist1")
    mock_query.find_track_recommendations.assert_called_once_with(
        "Track1", "Artist1", ["Feature1"], ["Structure1"]
    )
    mock_visualizer.create_network.assert_called_once_with(mock_query.find_track_recommendations.return_value)


#Post Tests for shortest path page
def test_post_shortest_path(test_client):
    client, mock_query, mock_visualizer = test_client

    mock_query.get_named_values.return_value = ["Artist1", "Artist2"]
    mock_query.shortest_path.return_value={
    "query_name": "shortest_path",
    "nodes": [
        {"id": "A1", "labels": ["Artist"], "properties": {"followers": 5000, "popularity": 50, "name": "Artist1", "id": "001"}},
        {"id": "A2", "labels": ["Artist"], "properties": {"followers": 5000, "popularity": 50, "name": "Artist2", "id": "002"}},
        {"id": "T1", "labels": ["Track"], "properties": {'duration_ms': 225640, 'explicit': False, 'name': 'Track1', 'track_number': 11, 'id': 'T1', 'artist_feature': 'A2'}},
    ],
    "edges": [
        {"id": 1, "type": "CREATED", "source": "A1", "target": "T1", "properties": {}},
        {"id": 2, "type": "FEATURES", "source": "T1", "target": "A2", "properties": {}},
    ]
    }


    response = client.post("/shortest_path", data={"artist_1_dropdown": "Artist1","artist_2_dropdown": "Artist2"},)
    
    assert response.status_code == 200
    assert b"Artist1" in response.data
    assert b"Artist2" in response.data
    
    mock_query.shortest_path.assert_called_once_with("Artist1","Artist2")
    mock_visualizer.create_network.assert_called_once_with(mock_query.shortest_path.return_value)


#Post Tests for shortest path page error
def test_post_shortest_path_error(test_client):
    client, mock_query, mock_visualizer = test_client

    mock_query.get_named_values.return_value = ["Artist1", "Artist2"]

    response = client.post(
        "/shortest_path",
        data={"artist_1_dropdown": "Artist1", "artist_2_dropdown": "Artist1"},
    )

    assert response.status_code == 200
    assert b"Error: Artist 2 can not be the same as Artist 1" in response.data

    mock_query.shortest_path.assert_not_called()
    mock_visualizer.create_network.assert_not_called()


#Post Tests for genre overlap page
def test_post_genre_overlap(test_client):
    client, mock_query, mock_visualizer = test_client

    mock_query.get_named_values.return_value = ["Genre1","Genre2"]
    mock_query.genre_overlap.return_value = {
    "query_name": "genre_overlap",
    "nodes": [
        {"id": "G1", "labels": ["Genre"], "properties": {"name": 'Genre1', 'id':'1'}},
        {"id": "G2", "labels": ["Genre"], "properties": {"name": 'Genre2', 'id':'2'}},
        {"id": "T1", "labels": ["Track"], "properties": {'duration_ms': 225640, 'explicit': False, 'name': 'Track1', 'track_number': 11, 'id': 'T1', 'artist_feature': 'A2'}},
        {"id": "T2", "labels": ["Track"], "properties": {'duration_ms': 555555, 'explicit': True, 'name': 'Track2', 'track_number': 1, 'id': 'T2', 'artist_feature': 'A3'}},
        {"id": "T3", "labels": ["Track"], "properties": {'duration_ms': 333333, 'explicit': False, 'name': 'Track3', 'track_number': 9, 'id': 'T3', 'artist_feature': 'A4'}},
    ],
    "edges": [
        {"id": 1, "type": "BELONGS_TO", "source": "T1", "target": "G1", "properties": {}},
        {"id": 2, "type": "BELONGS_TO", "source": "T1", "target": "G2", "properties": {}},
        {"id": 3, "type": "BELONGS_TO", "source": "T2", "target": "G1", "properties": {}},
        {"id": 4, "type": "BELONGS_TO", "source": "T2", "target": "G2", "properties": {}},
        {"id": 5, "type": "BELONGS_TO", "source": "T3", "target": "G1", "properties": {}},
        {"id": 6, "type": "BELONGS_TO", "source": "T3", "target": "G2", "properties": {}},
    ]
    }


    response = client.post("/genre_overlap", data={"genre_dropdown_1": "Genre1", "genre_dropdown_2": "Genre2"})

    assert response.status_code == 200
    assert b'Genre1' in response.data
    assert b'Genre2' in response.data
    
    mock_query.genre_overlap.assert_called_once_with('Genre1', 'Genre2')
    mock_visualizer.create_network.assert_called_once_with(mock_query.genre_overlap.return_value)


#Post Tests for genre overlap error page
def test_post_genre_overlap_error(test_client):
    client, mock_query, mock_visualizer = test_client

    mock_query.get_named_values.return_value = ["Genre1", "Genre2"]

    response = client.post(
        "/genre_overlap",
        data={"genre_dropdown_1": "Genre1", "genre_dropdown_2": "Genre1"},
    )

    assert response.status_code == 200
    assert b"Error: Genre 2 cannot be the same as Genre 1" in response.data

    mock_query.shortest_path.assert_not_called()
    mock_visualizer.create_network.assert_not_called()
