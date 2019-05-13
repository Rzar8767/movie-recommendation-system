from cassandra.cluster import Cluster
from src.ratings_cass_model import Rating
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
from cassandra.cqlengine import connection


class CassandraClient:
    def __init__(self):
        self.cluster = Cluster(['127.0.0.1'], port=9042)

        # should be connection pool, look it up
        self.session = self.cluster.connect()
        self.session.execute("CREATE KEYSPACE IF NOT EXISTS ratings_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};")
        connection.register_connection("cluster2", session=self.session, default=True)
        #drop_table(model=Rating)
        sync_table(model=Rating)


def dict_keys_to_underscores(obj):
    for key in obj.keys():
        new_key = key.replace("-","_")
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj


def dict_keys_from_underscores(obj):
    for key in obj.keys():
        key.replace("_", "-")
    return obj


if __name__ == '__main__':
    cassandra_client = CassandraClient()
    rating_dict = {"userID": 2,"movieID":1.0,"rating":3.0,"Action":0,"Adventure":0,"Animation":0,"Children":0,"Comedy":1,"Crime":0,"Documentary":0,"Drama":0,"Fantasy":0,"Film-Noir":0,"Horror":0,"IMAX":0,"Musical":0,"Mystery":0,"Romance":1,"Sci-Fi":0,"Short":0,"Thriller":0,"War":0,"Western":0}
    rating_dict = dict_keys_to_underscores(rating_dict)
    print(rating_dict)
    rating = Rating(**rating_dict)
    rating.save()
    rating_dict["userID"] = 3
    Rating.create(**rating_dict)
    q = Rating.objects()
    print(q.count())
    for i in q:
        print(dict(i))
    print(q)
    print(Rating.all())