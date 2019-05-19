import src.from_pandas as pandas_data
import json
import numpy
from src.cassandra_client import *



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


cassandra_client = CassandraClient()


class CassandraServerLogic:

    def __init__(self):
        pandas_data.empty_data_frame()

    def serialize_profile_vector(self, user_id):
        user = UserProfile.objects.filter(userID=user_id)
        if user.count() == 0:
            synchronize_cassandra()
            updated_profile = pandas_data.user_profile_vector(user_id)
            cass_profile = user_profile_to_cass(updated_profile)
            UserProfile(**cass_profile).save()
            serialized = json.dumps(updated_profile, cls=FloatEncoder)
        else:
            serialized = json.dumps(user_profile_from_cass(dict(user.first())))
        return serialized

    def serialize_genre_mean(self):
        synchronize_cassandra()
        serialized = json.dumps(pandas_data.get_movie_mean_by_genre(), cls=FloatEncoder)
        return serialized

    def serialize_data_frame(self):
        return cass_ratings_to_json_format(Rating.all())

    def delete_ratings(self):
        cassandra_client.clear_ratings()
        cassandra_client.clear_profiles()

    def add_row_to_data_frame(self, json_row):
        cass_rating = dict_keys_to_underscores(dict(json_row))
        Rating(**cass_rating).save()
        cassandra_client.clear_profiles()


def synchronize_cassandra():
    state = cass_ratings_to_json_format(Rating.all())
    pandas_data.JOINED_DF = pandas_data.from_json(state)