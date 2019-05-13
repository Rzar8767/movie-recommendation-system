import pandas
import flask
from flask import Response, request
import numpy
import json

from src.server_logic import ServerLogic


class FloatEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(FloatEncoder, self).default(obj)


my_app = flask.Flask(__name__)
server_logic = ServerLogic()


@my_app.route("/ratings", methods=['GET'])
def show_ratings():
    return Response(server_logic.serialize_data_frame(), status=200, mimetype='application/json')


@my_app.route('/rating', methods=['POST'])
def create_rating():
    new_row = request.get_json()
    server_logic.add_row_to_data_frame(new_row)
    response = json.dumps(new_row, cls=FloatEncoder)
    return Response(response, status=201, mimetype='application/json')


# Deletes the whole store
@my_app.route('/ratings', methods=['DELETE'])
def delete_ratings():
    server_logic.delete_ratings()
    return Response("{}", status=204, mimetype='application/json')


@my_app.route("/avg-genre-ratings/all-users", methods=['GET'])
def show_mean_ratings():
    return Response(server_logic.serialize_genre_mean(), status=200, mimetype='application/json')


@my_app.route("/avg-genre-ratings/<int:user_id>", methods=['GET'])
def show_mean_rating(user_id):
    return Response(server_logic.serialize_profile_vector(user_id), status=200, mimetype='application/json')


"""    username = request.args.get('username')
    password = request.args.get('password')"""

"""
@my_app.route("/ratings", methods=['POST'])
def add_rating():
    global user_rate_movies_genres
    user_rate_movies_genres = user_rate_movies_genres.append(json.loads(flask.request.data), ignore_index=True)
    return user_rate_movies_genres.to_json(orient='table', index=False)
"""
if __name__ == '__main__':
    my_app.run(host='0.0.0.0', port='4000')

