from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class Rating(Model):
    __keyspace__ = "ratings_keyspace"
    __table_name__ = "ratings"
    userID = columns.BigInt(primary_key=True)
    movieID = columns.BigInt(primary_key=True)
    rating = columns.Float()
    Action = columns.TinyInt()
    Adventure = columns.TinyInt()
    Animation = columns.TinyInt()
    Children = columns.TinyInt()
    Comedy = columns.TinyInt()
    Crime = columns.TinyInt()
    Documentary = columns.TinyInt()
    Drama = columns.TinyInt()
    Fantasy = columns.TinyInt()
    Film_Noir = columns.TinyInt()
    Horror = columns.TinyInt()
    IMAX = columns.TinyInt()
    Musical = columns.TinyInt()
    Mystery = columns.TinyInt()
    Romance = columns.TinyInt()
    Sci_Fi = columns.TinyInt()
    Short = columns.TinyInt()
    Thriller = columns.TinyInt()
    War = columns.TinyInt()
    Western = columns.TinyInt()

