from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class UserProfile(Model):
    __keyspace__ = "ratings_keyspace"
    __table_name__ = "user_profile"
    userID = columns.BigInt(primary_key=True)
    rating_Action = columns.Double()
    rating_Adventure = columns.Double()
    rating_Animation = columns.Double()
    rating_Children = columns.Double()
    rating_Comedy = columns.Double()
    rating_Crime = columns.Double()
    rating_Documentary = columns.Double()
    rating_Drama = columns.Double()
    rating_Fantasy = columns.Double()
    rating_Film_Noir = columns.Double()
    rating_Horror = columns.Double()
    rating_IMAX = columns.Double()
    rating_Musical = columns.Double()
    rating_Mystery = columns.Double()
    rating_Romance = columns.Double()
    rating_Sci_Fi = columns.Double()
    rating_Short = columns.Double()
    rating_Thriller = columns.Double()
    rating_War = columns.Double()
    rating_Western = columns.Double()

