from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class Rating(Model):
    __keyspace__ = "ratings_keyspace"
    __table_name__ = "ratings"
    userID = columns.BigInt(primary_key=True)
    movieID = columns.BigInt()
    rating = columns.Float()
    Action = columns.Boolean()
    Adventure = columns.Boolean()
    Animation = columns.Boolean()
    Children = columns.Boolean()
    Comedy = columns.Boolean()
    Crime = columns.Boolean()
    Documentary = columns.Boolean()
    Drama = columns.Boolean()
    Fantasy = columns.Boolean()
    Film_Noir = columns.Boolean()
    Horror = columns.Boolean()
    IMAX = columns.Boolean()
    Musical = columns.Boolean()
    Mystery = columns.Boolean()
    Romance = columns.Boolean()
    Sci_Fi = columns.Boolean()
    Short = columns.Boolean()
    Thriller = columns.Boolean()
    War = columns.Boolean()
    Western = columns.Boolean()

