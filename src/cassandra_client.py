from cassandra.cluster import Cluster
from src.ratings_cass_model import Rating
from src.profile_cass_model import UserProfile
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
from cassandra.cqlengine import connection
import src.from_pandas as panda
import json

class CassandraClient:
    def __init__(self):
        self.cluster = Cluster(['127.0.0.1'], port=9042)

        # should be connection pool, look it up
        self.session = self.cluster.connect()
        self.create_keyspace()
        connection.register_connection("cluster2", session=self.session, default=True)
        self.drop_profiles()
        #self.drop_ratings()
        sync_table(model=Rating)
        #sync_table(model=UserProfile)

    def create_keyspace(self):
        self.session.execute("CREATE KEYSPACE IF NOT EXISTS ratings_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};")

    def clear_table(self, keyspace, table):
        self.session.execute("TRUNCATE " + keyspace + "." + table + ";")

    def clear_profiles(self):
        #self.clear_table("ratings_keyspace", "user_profile")
        count = 3

    def clear_ratings(self):
        self.clear_table("ratings_keyspace", "ratings")

    def drop_profiles(self):
        drop_table(model=UserProfile)

    def drop_ratings(self):
        drop_table(model=Rating)



def dict_keys_to_underscores(obj):
    return replace_for_every(obj, "-", "_")


def dict_keys_from_underscores(obj):
    return replace_for_every(obj, "_", "-")


def replace_for_every(obj, phrase_before, phrase_after):
    new_dict = {}
    for key, value in obj.items():
        new_key = key.replace(phrase_before, phrase_after)
        new_dict[new_key] = value

    return new_dict


def user_profile_to_cass(obj):
    new_dict = {"userID": obj.pop("userID", None)}
    ratings_dict = dict_keys_to_underscores(obj['ratings'])
    for key, value in ratings_dict.items():
        new_dict["rating_" + key] = value
    return new_dict


def user_profile_from_cass(obj):
    new_dict = {"userID": obj.pop("userID", None)}
    new_dict['ratings'] = dict_keys_from_underscores(replace_for_every(obj, "rating_", ""))

    return new_dict


def cass_ratings_to_json_format(obj):
    new_dict = {}

    for index, row in enumerate(obj):
        new_dict[str(index)] = dict_keys_from_underscores(dict(row))
    return json.dumps(new_dict)


def test_conversions():
    rating_dict = {"userID": 2,"movieID":1.0,"rating":3.0,"Action":0,"Adventure":0,"Animation":0,"Children":0,"Comedy":1,"Crime":0,"Documentary":0,"Drama":0,"Fantasy":0,"Film-Noir":0,"Horror":0,"IMAX":0,"Musical":0,"Mystery":0,"Romance":1,"Sci-Fi":0,"Short":0,"Thriller":0,"War":0,"Western":0}
    rating_dict = dict_keys_to_underscores(rating_dict)
    print(rating_dict)
    rating = Rating(**rating_dict)
    print(dict_keys_from_underscores(dict(rating)))
    rating_dict["userID"] = 3
    profile = panda.user_profile_vector(75)
    print("Profile after creation: ")
    print(profile)

    print("Profile after conversion for cassandra: ")
    profile = user_profile_to_cass(profile)
    print(profile)

    print("Profile from cassandra model: ")
    profile_model = UserProfile(**profile)
    profile = dict(profile_model)
    print(profile)

    print("Profile for endpoint: ")
    profile2 = user_profile_from_cass(profile)
    print(profile2)


def test_db():
    cassandra_client = CassandraClient()
    rating_dict = {"userID": 2,"movieID":1.0,"rating":3.0,"Action":0,"Adventure":0,"Animation":0,"Children":0,"Comedy":1,"Crime":0,"Documentary":0,"Drama":0,"Fantasy":0,"Film-Noir":0,"Horror":0,"IMAX":0,"Musical":0,"Mystery":0,"Romance":1,"Sci-Fi":0,"Short":0,"Thriller":0,"War":0,"Western":0}
    rating_dict = dict_keys_to_underscores(rating_dict)
    print(rating_dict)
    rating = Rating(**rating_dict)
    print(dict_keys_from_underscores(dict(rating)))
    rating.save()
    rating_dict["movieID"] = 2
    Rating.create(**rating_dict)
    q = Rating.objects()
    print(q.count())
    for i in q:
        print(dict_keys_from_underscores(dict(i)))
    container = Rating.all()

    json_container = cass_ratings_to_json_format(container)
    print(json_container)

    print(panda.from_json(json_container))

if __name__ == '__main__':
    test_db()