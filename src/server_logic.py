import src.from_pandas as pandas_data
import json
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


class ServerLogic:

#Should return a json of {'userID': <number>, 'ratings': {'genre-name': <number>,...}} style

    def serialize_profile_vector(self, user_id):
        serialized = json.dumps(pandas_data.user_profile_vector(user_id), cls=FloatEncoder)
        return serialized

    def serialize_genre_mean(self):
        serialized = json.dumps(pandas_data.get_movie_mean_by_genre(), cls=FloatEncoder)
        return serialized

    def serialize_dataframe(self):
        serialized = pandas_data.JOINED_DF.to_json(orient='index')
        return serialized

    def delete_ratings(self):
        pandas_data.empty_dataframe()

    def add_row_to_dataframe(self, json_row):
        #dict_row = json.loads(json_row)
        pandas_data.add_row(json_row)




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
    print(server_logic.serialize_dataframe())
