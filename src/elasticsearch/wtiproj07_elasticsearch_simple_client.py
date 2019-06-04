import pandas as pd
from elasticsearch import Elasticsearch, helpers
import numpy as np


class ElasticClient:
    def __init__(self, address='localhost:10000'):
        self.es = Elasticsearch(address)

    # ------ Simple operations ------
    def index_documents(self):
        df = pd \
                 .read_csv('../../resources/user_ratedmovies.dat', delimiter='\t', nrows=200) \
                 .loc[:, ['userID', 'movieID', 'rating']]

        means = df.groupby(['userID'], as_index=False, sort=False) \
                    .mean() \
                    .loc[:, ['userID', 'rating']] \
            .rename(columns={'rating': 'ratingMean'})

        df = pd.merge(df, means, on='userID', how="left", sort=False)
        df['ratingNormal'] = df['rating'] - df['ratingMean']

        ratings = df.loc[:, ['userID', 'movieID', 'ratingNormal']] \
            .rename(columns={'ratingNormal': 'rating'}) \
            .pivot_table(index='userID', columns='movieID', values='rating') \
            .fillna(0)

        print("Indexing users...")
        index_users = [{
            "_index": "users",
            "_type": "user",
            "_id": index,
            "_source": {
                'ratings': row[row > 0] \
                    .sort_values(ascending=False) \
                    .index.values.tolist()
            }
        } for index, row in ratings.iterrows()]

        helpers.bulk(self.es, index_users, request_timeout=1000)
        print("Done")

        print("Indexing movies...")
        index_movies = [{
            "_index": "movies",
            "_type": "movie",
            "_id": column,
            "_source": {
                "whoRated": ratings[column][ratings[column] > 0] \
                    .sort_values(ascending=False) \
                    .index.values.tolist()
            }
        } for column in ratings]
        helpers.bulk(self.es, index_movies, request_timeout=1000)
        print("Done")

    def get_movies_liked_by_user(self, user_id, index='users'):
        user_id = int(user_id)
        return self.es.get(index=index, doc_type="user", id=user_id)["_source"]

    def get_users_that_like_movie(self, movie_id, index='movies'):
        movie_id = int(movie_id)
        return self.es.get(index=index, doc_type="movie", id=movie_id)["_source"]

    def get_preselection_for_user(self, user_id, index="users"):
        user_id = int(user_id)
        # Movies liked by user
        movies_rated = self.es.search(index=index, body=
        {
            "query": {
                "term":
                    {
                        "_id": user_id
                    }
            }
        })["hits"]["hits"][0]["_source"]["ratings"]

        # Movies of other people who liked at least one same movie
        similar_taste_movies = self.es.search(index=index, body=
        {
            "query": {
                "terms":
                    {
                        "ratings": movies_rated
                    }
            }
        })["hits"]["hits"]

        unique_movies = set()
        for ratings in similar_taste_movies:
            if ratings["_id"] != user_id:
                ratings = ratings["_source"]["ratings"]
                for rating in ratings:
                    # Do not recommend movies he's already seen
                    if rating not in movies_rated:
                        unique_movies.add(rating)
        return list(unique_movies)

    def get_preselection_for_movie(self, movie_id, index="movies"):
        movie_id = int(movie_id)

        # Users that liked movies
        users_liked = self.es.search(index=index, body=
        {
            "query": {
                "term":
                    {
                        "_id": movie_id
                    }
            }
        })["hits"]["hits"][0]["_source"]["whoRated"]

        # Users who have liked at least one other movie that this user liked
        similar_taste_users = self.es.search(index=index, body=
        {
            "query": {
                "terms":
                    {
                        "whoRated": users_liked
                    }
            }
        })["hits"]["hits"]

        unique_users = set()
        for whoRateds in similar_taste_users:
            if whoRateds["_id"] != movie_id:
                whoRateds = whoRateds["_source"]["whoRated"]
                for whoRated in whoRateds:
                    # Do not recommend movies he's already seen
                    if whoRated not in users_liked:
                        unique_users.add(whoRated)
        return list(unique_users)

    def add_user_document(self, user_id, movies_liked_by_user, user_index, movie_index):
        user_id = int(user_id)
        movies_liked_by_user = list(movies_liked_by_user)

        body = {'ratings': movies_liked_by_user}
        print("Body of added user: ", movies_liked_by_user)
        self.es.index(index=user_index, doc_type="user", id=user_id, body=body)
        self.add_user_to_movies(user_id, movies_liked_by_user)

    def add_movie_document(self, movie_id, users_who_like_movie, user_index, movie_index):
        movie_id = int(movie_id)
        users_who_like_movie = list(users_who_like_movie)

        body = {'whoRated': users_who_like_movie}
        print("Body of added document: ", users_who_like_movie)
        self.es.index(index=movie_index, doc_type="movie", id=movie_id, body=body)
        self.add_movie_to_users(movie_id, users_who_like_movie)

    def update_user_document(self, user_id, movies_liked_by_user, user_index, movie_index):
        user_id = int(user_id)
        body = {'doc': {'ratings': movies_liked_by_user}}
        self.es.update(index=user_index, doc_type="user", id=user_id, body=body)
        self.delete_user_from_movies([user_id])
        self.add_user_to_movies(user_id, movies_liked_by_user)

    def update_movie_document(self, movie_id, users_who_like_movie, user_index, movie_index):
        movie_id = int(movie_id)
        body = {'doc': {'whoRated': users_who_like_movie}}
        self.es.update(index=movie_index, doc_type="movie", id=movie_id, body=body)
        self.delete_movie_from_users([movie_id])
        self.add_movie_to_users(movie_id, users_who_like_movie)

    def delete_user_document(self, user_id, user_index, movie_index):
        # try:
        user_id = int(user_id)
        self.delete_user_from_movies([user_id])
        self.es.delete(index=user_index, doc_type="user", id=user_id)

    #  except helpers.errors.BulkIndexError as _bulk:
    #      return

    def delete_movie_document(self, movie_id, user_index, movie_index):
        try:
            movie_id = int(movie_id)
            self.delete_movie_from_users([movie_id])
            self.es.delete(index=movie_index, doc_type="movie", id=movie_id)
        except helpers.errors.BulkIndexError as _bulk:
            return

    def bulk_user_update(self, body, user_index):
        for user in body:
            user_id = user['user_id']
            movies_liked_by_user = user['liked_movies']
            self.update_user_document(user_id, movies_liked_by_user, user_index, 'movies')

    def bulk_movie_update(self, body, movie_index):
        for movie in body:
            movie_id = movie['movie_id']
            users_who_like_movie = movie['users_who_liked_movie']
            self.update_movie_document(movie_id, users_who_like_movie, 'users', movie_index)

    def add_movie_to_users(self, movie_id, users_who_like_movie):
        users_liking_movie = self.es.search(index="users", body=
        {
            "query": {
                "terms":
                    {
                        "_id": users_who_like_movie
                    }
            }
        })

        add_movie_to_users = [
            {
                "_id": user["_id"],
                "_type": "user",
                "_index": "users",
                "_source": {'doc': {'ratings': list(set(user["_source"]["ratings"].append(movie_id)))}},
                "_op_type": 'update'
            } for user in users_liking_movie['hits']['hits']
        ]

        helpers.bulk(self.es, add_movie_to_users, request_timeout=1000)

        for_creation = list()
        # if movie doesn't exist add it
        for user in users_liking_movie['hits']['hits']:
            for_creation.append(user['_id'])
        for id in for_creation:
            if id not in users_who_like_movie:
                self.add_user_document(id, [movie_id], 'users', 'movies')

    def delete_movie_from_users(self, movie_ids):
        users_who_liked_movie = self.es.search(index="users", body=
        {
            "query": {
                "terms":
                    {
                        "ratings": movie_ids
                    }
            }
        })

        delete_movie_from_users = [
            {
                "_id": user["_id"],
                "_type": "user",
                "_index": "users",
                "_source": {'doc': {'ratings': [e for e in user["_source"]["ratings"] if e not in movie_ids]}},
                "_op_type": 'update'
            } for user in users_who_liked_movie['hits']['hits']
        ]

        helpers.bulk(self.es, delete_movie_from_users, request_timeout=1000)

    def add_user_to_movies(self, user_id, movies_liked_by_user):

        try:
            movies_that_user_likes = self.es.search(index="movies", body=
            {
                "query": {
                    "terms":
                        {
                            "_id": movies_liked_by_user
                        }
                }
            })

            add_user_to_movies = [
                {
                    "_id": movie["_id"],
                    "_type": "movie",
                    "_index": "movies",
                    "_source": {'doc': {'whoRated': list(set(movie["_source"]["whoRated"].append(user_id)))}},
                    "_op_type": 'update'
                } for movie in movies_that_user_likes['hits']['hits']
            ]

            helpers.bulk(self.es, add_user_to_movies, request_timeout=1000)

            for_creation = list()
            # if movie doesn't exist add it
            for movie in movies_that_user_likes['hits']['hits']:
                for_creation.append(movie['_id'])
            for id in for_creation:
                if id not in movies_liked_by_user:
                    self.add_user_document(id, [user_id], 'users', 'movies')
        except TypeError:
            return

    def delete_user_from_movies(self, user_ids):
        movies_liked_by_users = self.es.search(index="movies", body=
        {
            "query": {
                "terms":
                    {
                        "ratings": user_ids
                    }
            }
        })

        delete_user_from_movies = [
            {
                "_id": movie["_id"],
                "_type": "movie",
                "_index": "movies",
                "_source": {'doc': {'whoRated': [e for e in movie["_source"]["whoRated"] if e not in user_ids]}},
                "_op_type": 'update'
            } for movie in movies_liked_by_users['hits']['hits']
        ]

        helpers.bulk(self.es, delete_user_from_movies, request_timeout=1000)

    def update_user_document_optimal(self, user_id, movies_liked_by_user, user_index, movie_index):
        user_id = int(user_id)

        movies_liked_before = self.es.search(index=user_index, body=
        {
            "query": {
                "term":
                    {
                        "_id": user_id
                    }
            }
        })["hits"]["hits"][0]["_source"]["ratings"]

        forgotten_movies = list(set(movies_liked_before).difference(set(movies_liked_by_user)))
        new_likes = list(set(movies_liked_by_user).difference(set(movies_liked_before)))


if __name__ == "__main__":
    ec = ElasticClient()
    ec.index_documents()

    # ------ Simple operations ------
    print()
    user_document = ec.get_movies_liked_by_user(75)
    movie_id = np.random.choice(user_document['ratings'])
    movie_document = ec.get_users_that_like_movie(movie_id)
    random_user_id = np.random.choice(movie_document['whoRated'])
    random_user_document = ec.get_movies_liked_by_user(random_user_id)

    print('User 75 likes following movies:')
    print(user_document)

    print('Movie {} is liked by following users:'.format(movie_id))
    print(movie_document)

    print('Is user 75 among users in movie {} document?'.format(movie_id))
    print(movie_document['whoRated'].index(75) != -1)

    import random

    some_test_movie_ID = 1
    print("Some test movie ID: ", some_test_movie_ID)
    print("The record for such movie ID:")
    print(ec.get_users_that_like_movie(some_test_movie_ID))
    list_of_users_who_liked_movie_of_given_ID = ec.get_users_that_like_movie(some_test_movie_ID)["whoRated"]
    print("List of users who liked the test movie: ", *list_of_users_who_liked_movie_of_given_ID)
    index_of_random_user_who_liked_movie_of_given_ID = random.randint(0, len(
        list_of_users_who_liked_movie_of_given_ID))

    print("Index of random user who liked the test movie: ", index_of_random_user_who_liked_movie_of_given_ID)
    some_test_user_ID = list_of_users_who_liked_movie_of_given_ID[index_of_random_user_who_liked_movie_of_given_ID]

    print("ID of random user who liked the test movie: ", some_test_user_ID)
    print("The record of this user:")
    print(ec.get_movies_liked_by_user(some_test_user_ID))
    movies_liked_by_user_of_given_ID = ec.get_movies_liked_by_user(some_test_user_ID)["ratings"]

    print("IDs of movies liked by the random user who liked the test movie: ", *movies_liked_by_user_of_given_ID)
    if some_test_movie_ID in movies_liked_by_user_of_given_ID:
        print("As expected, the test movie ID is among the IDs of movies " +
              "liked by the random user who liked the test movie ;-)")

    print("Get preselection for userID ", some_test_user_ID)
    print(ec.get_preselection_for_user(some_test_user_ID))

    print("Get preselection for movieID", some_test_movie_ID)
    print(ec.get_preselection_for_movie(some_test_movie_ID))

    print("Delete the fact users like movie of ID 1.")
  #  ec.delete_movie_from_users([some_test_movie_ID])
    print("Wait for indice refresh")
    ec.es.indices.refresh('users')
    # ec.es.cluster.health(wait_for_no_relocating_shards=True, wait_for_active_shards='all')
    print("Second run:")
    #ec.delete_movie_from_users([some_test_movie_ID])

    print("Get preselection for movieID again", some_test_movie_ID)
    print(ec.get_preselection_for_movie(some_test_movie_ID))
