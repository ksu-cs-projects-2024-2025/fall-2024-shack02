# GrooveMapper: Spotify Music Data Exploration App
## 1. Project Description
Explore music data using Spotify's API.
Visualize artist, track, and genre relationships.
Recommend tracks and artists based on user queries.
## 2. Installation Instructions
Steps to Set Up:
- Clone Repo
- Install dependencies: pip install -r requirements.txt
- Install Neo4j Desktop and create a new project with a local dbms
- Add Neo4j plugin APOC in Neo4j Desktop onto the local dbms that was created
- Input graph DBMS credentials into Neo4jQueryEngine
- Copy graph_data.csv from data folder in repository into C:..\.Neo4jDesktop\relate-data\dbmss\dbms-numbers\import folder
- Start the neo4j DBMS
- Run the groove_mapper.py file and enter y to load the dataset on first run. 
- Access the application via a browser (http://127.0.0.1:5000)

## 3. Application Architecture
Components:
* Neo4j Query Class (neo4j_query_library.py): Handles database interactions.
* Graph Visualization Class (graph_visualization.py): Generates PyVis visualizations.
* Groove Mapper Class (groove_mapper.py): Manages routing and API endpoints.
  * \routes contains Flask python endpoints
  * \static contains Pyvis graph html outputs
  * \templates contains Flask endpoint html
  * \tests contains api test file

Data Flow:
User Input → groove_mapper → neo4j_query_library → groove_mapper → graph_visualization → groove_mapper → Output to Browser.

## 4. Contact Information
Sean Hackenberg
Email: shack@ksu.edu
GitHub: https://github.com/shack02
