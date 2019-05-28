import requests
import time

host = "http://localhost:9898"


def get_ratings():
    resp = requests.get(url=host + "/ratings")
    return resp


def delete_ratings():
    resp = requests.delete(url=host + "/ratings")
    return resp


def post_rating(rating):
    resp = requests.post(url=host + "/rating", json=rating )
    return resp


def get_mean_ratings():
    resp = requests.get(url=host + "/avg-genre-ratings/all-users")
    return resp


def get_mean_user_rating(user_id):
    resp = requests.get(url=host + "/avg-genre-ratings/" + str(user_id))
    return resp


def get_user_vector(user_id):
    resp = requests.get(url=host + "/profile/" + str(user_id))
    return resp


def print_request(request):
    print("--------------------------------------------------------")
    print("request.url: " + str(request.url))
    print("request.status_code: " + str(request.status_code))
    print("request.headers: " + str(request.headers))
    print("request.text: " + request.text)
    print("request.request.body: " + str(request.request.body))
    print("request.request.headers: " + str(request.request.headers))
    print("--------------------------------------------------------")


if __name__ == '__main__':
    print("Client")

    print("Show the leftover contents: ")
    response = get_ratings()
    print_request(response)
    time.sleep(0.2)

    print("Delete the contents: ")
    response = delete_ratings()
    print_request(response)
    time.sleep(0.2)

    print("Show the contents: ")
    response = get_ratings()
    print_request(response)
    time.sleep(0.2)

    print("Get mean ratings, should be all 0")
    response = get_mean_ratings()
    print_request(response)
    time.sleep(0.2)

    print("Add a new rating")
    response = post_rating({"userID":2,"movieID":1.0,"rating":1.0,"Action":0,"Adventure":0,"Animation":0,"Children":0,"Comedy":1,"Crime":0,"Documentary":0,"Drama":0,"Fantasy":0,"Film-Noir":0,"Horror":0,"IMAX":0,"Musical":0,"Mystery":0,"Romance":1,"Sci-Fi":0,"Short":0,"Thriller":0,"War":0,"Western":0})
    print_request(response)
    time.sleep(0.2)

    print("Show the contents: ")
    response = get_ratings()
    print_request(response)
    time.sleep(0.2)

    print("Show user_id 2's mean rating: ")
    response = get_mean_user_rating(2)
    print_request(response)
    time.sleep(0.2)

    print("Show user_id 2's vector: ")
    response = get_user_vector(2)
    print_request(response)
    time.sleep(0.2)

    print("Add another rating")
    response = post_rating({"userID":2,"movieID":2.0,"rating":3.0,"Action":0,"Adventure":0,"Animation":0,"Children":0,"Comedy":1,"Crime":0,"Documentary":0,"Drama":0,"Fantasy":0,"Film-Noir":0,"Horror":0,"IMAX":0,"Musical":0,"Mystery":0,"Romance":1,"Sci-Fi":0,"Short":0,"Thriller":0,"War":0,"Western":0})
    print_request(response)
    time.sleep(0.2)

    print("Add another rating")
    response = post_rating({"userID":2,"movieID":3.0,"rating":3.0,"Action":0,"Adventure":0,"Animation":0,"Children":0,"Comedy":1,"Crime":0,"Documentary":0,"Drama":0,"Fantasy":0,"Film-Noir":0,"Horror":0,"IMAX":0,"Musical":0,"Mystery":0,"Romance":1,"Sci-Fi":0,"Short":0,"Thriller":0,"War":0,"Western":0})
    print_request(response)
    time.sleep(0.2)

    print("Add another rating")
    response = post_rating({"userID":3,"movieID":1.0,"rating":3.0,"Action":0,"Adventure":0,"Animation":0,"Children":0,"Comedy":1,"Crime":0,"Documentary":0,"Drama":0,"Fantasy":0,"Film-Noir":0,"Horror":0,"IMAX":0,"Musical":0,"Mystery":0,"Romance":1,"Sci-Fi":0,"Short":0,"Thriller":0,"War":0,"Western":0})
    print_request(response)
    time.sleep(0.2)

    print("Get mean ratings, should be 2.5 for Comedy")
    response = get_mean_ratings()
    print_request(response)
    time.sleep(0.2)

    print("Show user_id 2's mean rating, comedy should be 2.3333333333333335: ")
    response = get_mean_user_rating(2)
    print_request(response)
    time.sleep(0.2)

    print("Show user_id 2's vector, comedy should be -0.16666666666666652: ")
    response = get_user_vector(2)
    print_request(response)
    time.sleep(0.2)

    print("Show the contents: ")
    response = get_ratings()
    print_request(response)
    time.sleep(0.2)