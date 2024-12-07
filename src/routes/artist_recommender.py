from flask import Blueprint, render_template, request, jsonify, make_response

def create_blueprint(query, visualizer, node_limit):
    bp = Blueprint('artist_recommender', __name__, template_folder='templates')

    @bp.route('/artist_recommender')
    @bp.post('/artist_recommender')
    def artist_recommender():
        artist_options= query.get_named_values("Artist")
        selected_artist = request.cookies.get("selected_artist_recommender", None)
        if request.method == "POST":
            selected_artist = request.form.get('artist_dropdown')
            response = make_response(render_template("artist_recommender.html", title="Artist Recommender", artist_options=artist_options, selected_artist=selected_artist))
            response.set_cookie("selected_artist_recommender", selected_artist)
            graph_data = query.find_artist_recommendations(selected_artist)
            visualizer.create_network(graph_data)
            return response

        return render_template("artist_recommender.html", title="Artist Recommender",artist_options = artist_options, selected_artist = selected_artist)
    
    return bp