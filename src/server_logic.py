import src.from_pandas as pandas_data
import json
import numpy
from src.redis_client import QueueRedis
from enum import Enum

redis_pool = QueueRedis()


class DataSource(Enum):
    FILE = 1
    REDIS = 2


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


class ServerLogic:

    def __init__(self):
        self.mode = DataSource.REDIS

        if self.mode == DataSource.REDIS:
            pandas_data.empty_data_frame()
            pandas_data.JOINED_DF = pandas_data.from_json(redis_pool.get("ratings").decode("utf-8"))

    #Should return a json of {'userID': <number>, 'ratings': {'genre-name': <number>,...}} style

    def serialize_profile_vector(self, user_id):
        if self.mode == DataSource.FILE or DataSource.REDIS:
            serialized = json.dumps(pandas_data.user_profile_vector(user_id), cls=FloatEncoder)
            return serialized

    def serialize_genre_mean(self):
        if self.mode == DataSource.FILE or DataSource.REDIS:
            serialized = json.dumps(pandas_data.get_movie_mean_by_genre(), cls=FloatEncoder)
            return serialized

    def serialize_data_frame(self):
        if self.mode == DataSource.FILE:
            serialized = pandas_data.JOINED_DF.to_json(orient='index')
            return serialized
        if self.mode == DataSource.REDIS:
            return redis_pool.get("ratings").decode("utf-8")

    def delete_ratings(self):
        if self.mode == DataSource.FILE:
            pandas_data.empty_data_frame()
        if self.mode == DataSource.REDIS:
            pandas_data.empty_data_frame()
            redis_pool.set("ratings", "{}")

    def add_row_to_data_frame(self, json_row):
        if self.mode == DataSource.FILE:
            pandas_data.add_row(json_row)
        if self.mode == DataSource.REDIS:
            pandas_data.add_row(json_row)
            to_redis = pandas_data.JOINED_DF.to_json(orient='index')
            redis_pool.set("ratings", to_redis)




"""
Potrzeba przechować:
    - całą tabelę z genre
        tak aby móc dodawać nowe rekordy
        tak aby móc ją całkowicie wyczyścić
    - vector profili użytkowników
        tak aby po dodaniu nowego rekordu aktualizował się
"""

if __name__ == '__main__':
    server_logic = ServerLogic()
    print("Print json profile vector of user 75: ")
    print(server_logic.serialize_profile_vector(75))
    print("Print json mean of genre ratings: ")
    print(server_logic.serialize_genre_mean())
    print(server_logic.serialize_data_frame())

    redis_ratings = pandas_data.JOINED_DF.to_json(orient='index')
    print(redis_ratings)
    redis_pool.set("ratings", redis_ratings)
    print("Before loading:")
    pandas_data.empty_data_frame()
    print(pandas_data.JOINED_DF)

    print("After loading:")
    pandas_data.JOINED_DF = pandas_data.from_json(redis_pool.get("ratings").decode("utf-8"))
    print(pandas_data.JOINED_DF)
