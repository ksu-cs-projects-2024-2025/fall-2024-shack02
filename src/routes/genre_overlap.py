from flask import Blueprint, render_template, request, jsonify, make_response

def create_blueprint(query, visualizer, node_limit):
    bp = Blueprint('genre_overlap', __name__, template_folder='templates')

    @bp.route('/genre_overlap')
    @bp.post('/genre_overlap')
    def genre_overlap():
        genre_options = query.get_named_values("Genre")
        genre_1 = request.cookies.get("genre_1", None)
        genre_2 = request.cookies.get("genre_2", None)
        if request.method == "POST":
            genre_1 = request.form.get("genre_dropdown_1")
            genre_2 = request.form.get("genre_dropdown_2")
        
            if genre_1 == genre_2:
                error_message = "Error: Genre 2 cannot be the same as Genre 1"
                return render_template(
                    "genre_overlap.html", 
                    title="Genre Overlap Graph", 
                    genre_options=genre_options, 
                    genre_1=genre_1, 
                    genre_2=genre_2,
                    error_message=error_message
                )
            response = make_response(render_template("genre_overlap.html", title="Genre Overlap Graph", genre_options=genre_options, genre_1=genre_1, genre_2=genre_2))

            response.set_cookie("genre_1", genre_1)
            response.set_cookie("genre_2", genre_2)
            
            graph_data = query.genre_overlap(genre_1, genre_2)
            visualizer.create_network(graph_data)
            
            return response

        return render_template("genre_overlap.html", title="Genre Overlap Graph", genre_options=genre_options, genre_1=genre_1, genre_2=genre_2)

    
    return bp