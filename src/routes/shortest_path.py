from flask import Blueprint, render_template, request

def create_blueprint(query, visualizer, node_limit):
    bp = Blueprint('shortest_path', __name__, template_folder='templates')

    @bp.route('/shortest_path')
    @bp.post('/shortest_path')
    @bp.get('/shortest_path')
    def shortest_path():
        artist_options = query.get_named_values("Artist")
        artist_1 = None
        artist_2 = None
        if request.method == "POST":
            artist_1 = request.form.get("artist_1_dropdown")
            artist_2 = request.form.get("artist_2_dropdown")
            if artist_1 == artist_2:
                return render_template("shortest_path.html", title ="Artist to Artist Pathfinding", artist_options=artist_options, artist_1 = artist_1, artist_2 = artist_2, error_message = "Error: Artist 2 can not be the same as Artist 1")
            graph_data = query.shortest_path(artist_1,artist_2)
            visualizer.create_network(graph_data)
        return render_template("shortest_path.html", title ="Artist to Artist Pathfinding", artist_options=artist_options, artist_1 = artist_1, artist_2 = artist_2)
    return bp