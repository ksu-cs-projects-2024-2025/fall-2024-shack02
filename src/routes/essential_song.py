from flask import Blueprint, render_template, request, make_response

def create_essential_song_blueprint(query, visualizer, node_limit):
    essential_bp = Blueprint('essential_song', __name__, template_folder='templates')

    @essential_bp.route('/essential_song')
    @essential_bp.post('/essential_song')
    @essential_bp.get('/essential_song')
    def essential_song():
        artist_options = query.get_named_values("Artist")
        selected_artist = request.cookies.get("selected_artist", None)
        if request.method == "POST":
            selected_artist = request.form.get("artist_dropdown")
            response = make_response(render_template("essential_song.html", title="Essential Song", artist_options=artist_options, selected_artist=selected_artist))
            response.set_cookie("selected_artist", selected_artist)
            graph_data = query.essential_track(selected_artist)
            visualizer.create_network(graph_data)
            return response
        
        return render_template("essential_song.html", title="Essential Song", artist_options=artist_options, selected_artist = selected_artist)
    return essential_bp