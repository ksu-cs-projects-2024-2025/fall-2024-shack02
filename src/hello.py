from flask import Flask, render_template, request
from pyvis.network import Network
from neo4j import GraphDatabase
from neo4j_query_library import Neo4jQueryEngine
from graph_visualization import GraphVisualizer
import os


class GrooveMapper():
  def __init__(self):
      self.app = Flask(__name__)
      self.query = Neo4jQueryEngine()
      self.visualizer = GraphVisualizer()
      self.node_limit = 100
      self.routes()
      
  #Defines the routes for the different pages
  def routes(self):
    @self.app.route('/')
    @self.app.route('/home')
    def home():
        return self.home()
    
    @self.app.route('/about')
    def about():
       return self.about()
    
    @self.app.route('/essential_song')
    @self.app.post('/essential_song')
    def essential_song():
       return self.essential_song()
      
  #Defines the homepage and orchestrates the base query
  def home(self):
      graph_data = self.query.fetch_graph_data(self.node_limit)
      self.visualizer.create_home_network(graph_data)
      return render_template("home.html", title="Home")

  #Defines the about page
  def about(self):
      return render_template("about.html", title="About")

  def essential_song(self):
      artist_options = self.query.get_artists()
      print(artist_options)
      features = self.query.get_track_features()
      print(features)
      
      selected_artist = None
      if request.method == "POST":
        selected_artist = request.form.get("artist_dropdown")
        graph_data = self.query.essential_track(selected_artist, self.node_limit)
        self.visualizer.create_essential_network(graph_data)

      return render_template("essential_song.html", title="Essential Song", artist_options=artist_options)
  
  def run(self):
      self.app.run(debug=True, host='127.0.0.1', port=5001)

if __name__ == "__main__":
  groove_mapper = GrooveMapper()
  groove_mapper.run()
