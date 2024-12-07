from flask import Flask, render_template, request, jsonify, Blueprint
from pyvis.network import Network
from neo4j import GraphDatabase
from neo4j_query_library import Neo4jQueryEngine
from graph_visualization import GraphVisualizer
from routes.home import create_home_blueprint
from routes.essential_song import create_essential_song_blueprint
from routes.genre_overlap import create_blueprint as create_genre_overlap_blueprint
from routes.shortest_path import create_blueprint as create_shortest_path_blueprint
from routes.track_recommender import create_blueprint as create_track_recommender_blueprint
from routes.artist_recommender import create_blueprint as create_artist_recommender_blueprint
import os

#This class acts as the controller. It instantiates the Neo4jQueryEngine and GraphVisualizer classes and then uses these classes in the Flask API route blueprints
class GrooveMapper():
  def __init__(self):
      self.app = Flask(__name__)
      self.query = Neo4jQueryEngine()
      self.visualizer = GraphVisualizer()
      self.node_limit = 50
      self.register_blueprints()
  
  def register_blueprints(self):
     home_bp = create_home_blueprint(self.query, self.visualizer, self.node_limit)
     essential_bp = create_essential_song_blueprint(self.query, self.visualizer, self.node_limit)
     genre_overlap_bp = create_genre_overlap_blueprint(self.query, self.visualizer, self.node_limit)
     shortest_path_bp = create_shortest_path_blueprint(self.query, self.visualizer, self.node_limit)
     track_recommender_bp = create_track_recommender_blueprint(self.query, self.visualizer, self.node_limit)
     artist_recommender_bp = create_artist_recommender_blueprint(self.query,self.visualizer,self.node_limit)

     self.app.register_blueprint(home_bp)
     self.app.register_blueprint(essential_bp)
     self.app.register_blueprint(genre_overlap_bp)
     self.app.register_blueprint(shortest_path_bp)
     self.app.register_blueprint(track_recommender_bp)
     self.app.register_blueprint(artist_recommender_bp)

  def run(self):
      self.app.run(debug=True, host='127.0.0.1', port=5001)

if __name__ == "__main__":
  groove_mapper = GrooveMapper()
  groove_mapper.run()
