from flask import Blueprint, render_template, request

def create_blueprint(query, visualizer, node_limit):
    bp = Blueprint('genre_overlap', __name__, template_folder='templates')

    @bp.route('/genre_overlap')
    @bp.post('/genre_overlap')
    def genre_overlap():
        genre_options = query.get_named_values("Genre")
        genre_1 = request.form.get("genre_dropdown_1")
        genre_2 = request.form.get("genre_dropdown_2")
        if request.method == "POST":
            graph_data = query.genre_overlap(genre_1,genre_2)
            visualizer.create_genre_overlap_graph(graph_data)

        return render_template("genre_overlap.html", title="Genre Overlap Graph", genre_options = genre_options, genre_1=genre_1,genre_2=genre_2)
    return bp