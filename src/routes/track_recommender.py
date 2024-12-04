from flask import Blueprint, render_template, request, jsonify

def create_blueprint(query, visualizer, node_limit):
    bp = Blueprint('track_recommender', __name__, template_folder='templates')

    @bp.route('/track_recommender')
    @bp.post('/track_recommender')
    @bp.get('/track_recommender')
    def track_recommendations():
        genre_options= query.get_named_values("Genre")
        artist_options= query.get_named_values("Artist")
        # track_options = []
        track_feature_options = query.track_features
        track_structure_options = query.track_structure
        selected_artist = "702"
        selected_track = None
        selected_genre = None
        selected_track_features = []
        selected_track_structures = []
        if request.method == "POST":
            selected_artist = request.form.get('artist_dropdown')
            selected_track = request.form.get('track_dropdown')
            selected_genre = request.form.get('genre_dropdown')
            selected_track_features = request.form.getlist("track_features")
            selected_track_structures = request.form.getlist("track_structures")
            track_recommendation_data = query.find_track_recommendations(selected_track,selected_artist,selected_genre,selected_track_features,selected_track_structures)
            print(track_recommendation_data)
            visualizer.create_track_recommendations_graph(track_recommendation_data)
        return render_template("track_recommender.html", title="Track Recommender", genre_options =genre_options, 
                                                                                    artist_options = artist_options, 
                                                                                    track_options = query.get_tracks_for_artist(selected_artist), 
                                                                                    track_feature_options= track_feature_options, 
                                                                                    track_structure_options = track_structure_options,
                                                                                    selected_artist = selected_artist,
                                                                                    selected_genre = selected_genre,
                                                                                    selected_track=selected_track,
                                                                                    selected_track_features = selected_track_features,
                                                                                    selected_track_structures=selected_track_structures)
                                                            
    @bp.route("/artist_track_lists", methods=["POST"])
    def artist_track_lists():
       artist = request.form.get("artist_dropdown")
       return jsonify({"track_options": query.get_tracks_for_artist(artist)})
    


    return bp