from flask import Blueprint, render_template, request, jsonify

def create_blueprint(query, visualizer, node_limit):
    bp = Blueprint('artist_recommender', __name__, template_folder='templates')

    @bp.route('/artist_recommender')
    @bp.post('/artist_recommender')
    def artist_recommender():
        genre_options= query.get_named_values("Genre")
        artist_options= query.get_named_values("Artist")
        track_options = []
        track_feature_options = query.track_features
        track_structure_options = query.track_structure

        if request.method == "POST":
            selected_artist = request.form.get('artist_dropdown')
            selected_track = request.form.get('track_dropdown')
            selected_genre = request.form.get('genre_dropdown')
            selected_track_features = request.form.getlist("track_features")
            selected_track_structures = request.form.getlist("track_structures")
            track_recommendation_data = query.find_track_recommendations(selected_track,selected_artist,selected_genre,selected_track_features,selected_track_structures)
            print(track_recommendation_data)
        return render_template("track_recommender.html", title="Track Recommender", genre_options =genre_options, 
                            artist_options = artist_options, track_options = track_options, track_feature_options= track_feature_options, 
                            track_structure_options = track_structure_options)
    
    return bp