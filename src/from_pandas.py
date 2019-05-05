import pandas as pd
import numpy as np
import json
import math


def get_rated_movies_df(_nrows = None):
    rated_movies_df = pd.read_csv("../resources/user_ratedmovies.dat", header=0,
                                  delimiter="\t", usecols=['userID', 'movieID', 'rating'],
                                  dtype={'userID': np.uint64, 'movieID': np.uint64, 'rating': np.float32},
                                  nrows=_nrows)
    return rated_movies_df


def get_movie_genres_df(_nrows = None):
    movie_genres_df = pd.read_csv("../resources/movie_genres.dat", header=0,
                                  delimiter="\t", usecols=['movieID', 'genre'],
                                  dtype={'movieID': np.uint64, 'genre': np.str},
                                  nrows=_nrows)
    return movie_genres_df


UNIQUE_GENRES = get_movie_genres_df().genre.unique()


def get_joined():
    joined_df = pd.read_csv("../resources/joined.dat", header=0, delimiter="\t",
                            dtype={'userID': np.uint64, 'movieID': np.uint64, 'rating': np.float32})
    return joined_df


# returns column names of genres
def user_rated_movies_with_genres(rated_movies_df, movie_genres_df):

    genres_column_names = movie_genres_df.genre.unique()
    print(genres_column_names)
    movie_genres_df['dummy_column'] = 1
    print(movie_genres_df.head(2))
    # przestaw kolumny i wiersze
    movie_genres_df_pivoted = movie_genres_df.pivot_table(index="movieID", columns="genre", fill_value=0, values="dummy_column")

    # movie_genres_df_pivoted = movie_genres_df_pivoted.fillna(0)
    movie_genres_df_pivoted = movie_genres_df_pivoted.astype(int)

    joined_df = pd.merge(rated_movies_df, movie_genres_df_pivoted, on='movieID')

    joined_df.to_csv("../resources/joined.dat", sep="\t", index=False)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(joined_df)

    return genres_column_names


JOINED_DF = get_joined()


def add_row(row):
    global JOINED_DF
    JOINED_DF = JOINED_DF.append(row, ignore_index=True)


def empty_dataframe():
    global JOINED_DF
    JOINED_DF = JOINED_DF.iloc[0:0]
    #JOINED_DF.loc[0 if math.isnan(JOINED_DF.index.max()) else JOINED_DF.index.max() + 1] = JOINED_DF


# changes the data frame into list of dicts
def df_to_list_of_dict(df):
    list_of_dicts = []

    for index, row in df.iterrows():
        list_of_dicts.append(json.loads(row.to_json()))

    return list_of_dicts


def df_from_list_of_dict(lod):
    order_cols = get_joined().columns.tolist()
    df = pd.DataFrame(lod)[order_cols]
    cols = [i for i in df.columns if i not in ["rating"]]
    for col in cols:
        df[col] = pd.to_numeric(df[col], downcast="unsigned")
    return df


#mean rating of movie genres
def get_movie_mean_by_genre():
    joined_df = JOINED_DF

    #print(joined_df[joined_df["Action"] == 1])
    #print(joined_df[joined_df.Action == 1])

    avg_by_genre = {}

    for genre in UNIQUE_GENRES:
        avg_by_genre[genre] = joined_df[joined_df[genre] == 1].rating.mean()
        if np.isnan(avg_by_genre[genre]):
            avg_by_genre[genre] = 0.0
    return avg_by_genre


#mean rating of movie genres given by user
def get_user_mean_by_genre(user_id):
    joined_df = JOINED_DF

    avg_by_genre_usr = {"userID:": user_id, "ratings": {}}

    avg_rating = {}

    for genre in UNIQUE_GENRES:
        avg_rating[genre] = joined_df.loc[(joined_df[genre] == 1) & (joined_df['userID'] == user_id)].rating.mean()
        if np.isnan(avg_rating[genre]):
            avg_rating[genre] = 0.0
    avg_by_genre_usr["ratings"] = avg_rating
    return avg_by_genre_usr


def user_profile_vector(user_id):
    genre_rating = get_movie_mean_by_genre()
    user_rating = get_user_mean_by_genre(user_id)

    for genre in UNIQUE_GENRES:
        user_rating['ratings'][genre] -= genre_rating[genre]
        if np.isnan(user_rating['ratings'][genre]):
            user_rating['ratings'][genre] = 0.0
    return user_rating


if __name__ == '__main__':
    #rated_movies_df = get_rated_movies_df(500).astype(object)
    #movie_genres_df = get_movie_genres_df().astype(object)

    #joined_df = user_rated_movies_with_genres(rated_movies_df, movie_genres_df)

    #x = (df_to_list_of_dict(get_joined()))
    #print(df_from_list_of_dict(x))
    print("Print the mean ratings for all genres: ")
    print(get_movie_mean_by_genre())
    print("Print user 75's mean ratings for all genres: ")
    print(get_user_mean_by_genre(75))
    print("Print user 75's profile vector: ")
    print(user_profile_vector(75))

    #print(avg_rating_by_genre_by_user_id(75, 1414))