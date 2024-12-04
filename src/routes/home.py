from flask import Blueprint, render_template, request

def create_home_blueprint(query, visualizer, node_limit):
    home_bp = Blueprint('home', __name__, template_folder='templates')

    @home_bp.route('/')
    @home_bp.route('/home')
    def home():
        graph_data = query.fetch_graph_data(node_limit)
        visualizer.create_network(graph_data)
        return render_template('home.html', title='Home')

    @home_bp.route('/about')
    def about():
        return render_template('about.html', title='About')

    return home_bp