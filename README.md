# Movie Recommendation System

A movie recommendation engine built as a learning project for the *Selected Information
Technologies* (Wybrane Technologie Informatyczne) course, part of the Computer Science engineering program at Poznań University
of Technology.

The system ingests user movie ratings and genre data, builds per-user genre preference
profiles, and uses collaborative filtering to preselect and recommend movies a user is
likely to enjoy — exposed via a REST API and backed by Cassandra, Elasticsearch, and Redis.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core language for all services and data processing |
| Pandas / NumPy | Data loading, transformation, and profile-vector computation |
| Apache Cassandra | Primary datastore for ratings and user profiles |
| Elasticsearch | Indexing and fast preselection of candidate movies/users |
| Redis | In-memory caching/queueing of ratings data |
| Flask | REST API layer |
| CherryPy | WSGI server hosting the Flask app |
| Requests | HTTP client used for calling the API |
| Postman | Manual API testing collection |

## Getting Started

### 1. Install dependencies

```bash
pip install pandas numpy flask requests redis cassandra-driver "elasticsearch>=6.0.0,<7.0.0" cheroot
```

### 2. Start the backing services (Docker)

**Cassandra** — primary datastore for ratings/user profiles
```bash
sudo docker run --name main_cass -p 9042:9042 \
  -e HEAP_NEWSIZE=100M -e MAX_HEAP_SIZE=1024M --rm cassandra:latest
```

**Elasticsearch** — indexing/preselection layer
```bash
sudo docker run --network host --name elastic --rm \
  -e "http.port=10000" -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:6.6.2
```

**Redis** — in-memory cache/queue
```bash
sudo docker run --name redisq --network host --rm redis:latest --port 6381
```

### 3. Initialize Cassandra schema

Connect to the Cassandra container and open `cqlsh`:
```bash
sudo docker exec -it main_cass bash
cqlsh
```

Then create the keyspace (tables are also created automatically at app startup via `cassandra_client.py`):
```sql
CREATE KEYSPACE IF NOT EXISTS ratings_keyspace
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```

### 4. Run the API server

```bash
python -m src.cherrypy_server
```
This serves the Flask app (`src/flask_api.py`) via CherryPy/Cheroot's WSGI server on `http://localhost:9898`.

> Alternatively, for local development you can run Flask directly (`python -m src.flask_api`), which listens on port `4000`.

### 5. Available endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/ratings` | Get all ratings |
| POST | `/rating` | Add a new rating |
| DELETE | `/ratings` | Delete all ratings |
| GET | `/avg-genre-ratings/all-users` | Average genre ratings across all users |
| GET | `/avg-genre-ratings/<user_id>` | Average genre ratings for one user |
| GET | `/profile/<user_id>` | Get a user's genre profile vector |

The Elasticsearch service (`src/elasticsearch/wtiproj07_api.py`) exposes a separate API for preselection:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/user/document/<id>` | Movies liked by a user |
| GET | `/movie/document/<id>` | Users who liked a movie |
| GET | `/user/preselection/<id>` | Preselected movie candidates for a user (collaborative filtering) |

### 6. Testing

A Postman collection is available for manual API testing:
https://www.getpostman.com/collections/50495e4581cc2fd60dc8
