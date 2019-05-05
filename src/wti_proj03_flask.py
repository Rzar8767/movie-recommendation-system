import pandas
import flask
from flask import Response, request
import json
import from_pandas as data
import numpy


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


@my_app.route("/ratings", methods=['GET'])
def show_ratings():
    return Response(data.JOINED_DF.to_json(orient='index'), status=200, mimetype='application/json')


"""
@my_app.route('/ratings', methods=['POST'])
def create_rating():
    return Response(zad1.add(request.data), status=201, mimetype='application/json')
"""


# Deletes the whole store
@my_app.route('/ratings', methods=['DELETE'])
def delete_rating():
    #index = request.args.get('index', False)
    Response("{}", status=204, mimetype='application/json')


@my_app.route("/mean_genre_ratings", methods=['GET'])
def show_mean_ratings():
    return Response(json.dumps(data.get_movie_mean_by_genre(), cls=FloatEncoder), status=200, mimetype='application/json')


@my_app.route("/ratings/<int:user_id>", methods=['GET'])
def show_rating(user_id):
    df_for_user = data.JOINED_DF.loc[data.JOINED_DF['userID'] == user_id]
    print(df_for_user)
    return Response(df_for_user.to_json(orient='index'), status=200, mimetype='application/json')


@my_app.route("/mean_genre_ratings/<int:user_id>", methods=['GET'])
def show_mean_rating(user_id):
    return Response(json.dumps(data.get_user_mean_by_genre(user_id), cls=FloatEncoder), status=200, mimetype='application/json')


"""    username = request.args.get('username')
    password = request.args.get('password')"""

"""
@my_app.route("/ratings", methods=['POST'])
def add_rating():
    global user_rate_movies_genres
    user_rate_movies_genres = user_rate_movies_genres.append(json.loads(flask.request.data), ignore_index=True)
    return user_rate_movies_genres.to_json(orient='table', index=False)
"""

my_app.run(host='0.0.0.0', port='4000')
