from flask import Flask, render_template
from pyvis.network import Network
import os

app = Flask(__name__)

def create_network():
    from flask import Flask, render_template
from pyvis.network import Network

app = Flask(__name__)

def create_network():
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False)

    # Add nodes and edges
    net.add_node(1, label="Node 1")
    net.add_node(2, label="Node 2")
    net.add_edge(1, 2)

    # Generate the HTML for the network
    if not os.path.exists("static"):
        os.makedirs("static")

    net.generate_html("static/network.html")
    net.show("static/network.html", notebook=False)

@app.route('/')
def index():
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)