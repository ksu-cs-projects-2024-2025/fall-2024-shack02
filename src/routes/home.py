from flask import Blueprint, render_template, request, make_response

def create_home_blueprint(query, visualizer, node_limit):
    home_bp = Blueprint('home', __name__, template_folder='templates')

    @home_bp.route('/')
    @home_bp.route('/home')
    @home_bp.post('/home')
    def home():
        artist_options = query.get_named_values("Artist")
        selected_artist = request.cookies.get("selected_artist_home", None)
        if request.method == "POST":
            selected_artist = request.form.get("artist_dropdown")
            response = make_response(render_template("home.html", title="Home", artist_options=artist_options, selected_artist=selected_artist))
            response.set_cookie("selected_artist_home", selected_artist)
            graph_data = query.home_graph(selected_artist)
            visualizer.create_network(graph_data)
            return response
        return render_template('home.html', title='Home', artist_options=artist_options, selected_artist = selected_artist)

    return home_bp