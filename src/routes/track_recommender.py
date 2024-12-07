from flask import Blueprint, render_template, request, jsonify, make_response
import json

def create_blueprint(query, visualizer, node_limit):
    bp = Blueprint('track_recommender', __name__, template_folder='templates')

    @bp.route('/track_recommender')
    @bp.post('/track_recommender')
    @bp.get('/track_recommender')
    def track_recommendations():
        artist_options= query.get_named_values("Artist")
        track_feature_options = query.track_features
        track_structure_options = query.track_structure

        selected_artist = request.cookies.get("selected_artist_track_recommender", None)
        selected_track = request.cookies.get("selected_track_track_recommender", None)
        selected_track_features_str = request.cookies.get("selected_track_features_track_recommender", [])
        selected_track_structures_str = request.cookies.get("selected_track_structures_track_recommender", [])

        if selected_track_features_str != []:
            selected_track_features = json.loads(selected_track_features_str)
        else: selected_track_features = []

        if selected_track_structures_str != []:
            selected_track_structures = json.loads(selected_track_structures_str)
        else: selected_track_structures = []

        if request.method == "POST":
            selected_artist = request.form.get('artist_dropdown')
            selected_track = request.form.get('track_dropdown')
            selected_track_features = request.form.getlist("track_features")
            selected_track_structures = request.form.getlist("track_structures")

            response = make_response(render_template("track_recommender.html", title="Track Recommender", artist_options = artist_options, 
                                                                                    track_options = query.get_tracks_for_artist(selected_artist), 
                                                                                    track_feature_options= track_feature_options, 
                                                                                    track_structure_options = track_structure_options,
                                                                                    selected_artist = selected_artist,
                                                                                    selected_track=selected_track,
                                                                                    selected_track_features = selected_track_features,
                                                                                    selected_track_structures=selected_track_structures))
            response.set_cookie("selected_artist_track_recommender", selected_artist)
            response.set_cookie("selected_track_track_recommender", selected_track)
            response.set_cookie("selected_track_features_track_recommender", json.dumps(selected_track_features))
            response.set_cookie("selected_track_structures_track_recommender", json.dumps(selected_track_structures))

            track_recommendation_data = query.find_track_recommendations(selected_track,selected_artist,selected_track_features,selected_track_structures)
            visualizer.create_network(track_recommendation_data)
            return response
        return render_template("track_recommender.html", title="Track Recommender", artist_options = artist_options, 
                                                                                    track_options = query.get_tracks_for_artist(selected_artist), 
                                                                                    track_feature_options= track_feature_options, 
                                                                                    track_structure_options = track_structure_options,
                                                                                    selected_artist = selected_artist,
                                                                                    selected_track=selected_track,
                                                                                    selected_track_features = selected_track_features,
                                                                                    selected_track_structures=selected_track_structures)
                                                            
    @bp.route("/artist_track_lists", methods=["POST"])
    def artist_track_lists():
       artist = request.form.get("artist_dropdown")
       return jsonify({"track_options": query.get_tracks_for_artist(artist)})
    


    return bp