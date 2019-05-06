import redis
import json


class QueueRedis:

    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6381, db=0)
        self.pool = redis.ConnectionPool(host='localhost', port=6381, db=0)

    def conn(self):
        return redis.Redis(connection_pool=self.pool)

    def _add(self, name, value):
        """
        Add to queue or extend value
        :param name: name queue
        :param value: value to add to queue
        """
        return self.r.rpush(name, value)

    def _get(self, name, start=0, stop=-1):
        """
        Returns the specified elements of the list stored at name.
        :param name: name queue
        :param start: start of range
        :param stop: stop of range
        :return:
        """
        return self.r.lrange(name, start, stop)

    def get(self, name):
        #return self.r.get(name)
        return self.conn().get(name)

    def set(self, name, value):
        #return self.r.set(name)
        return self.conn().set(name, value)

    def exists(self, name):
        return self.conn().exists(name)

    def _flushdb(self):
        """
        Delete all the keys of the currently selected DB
        :return: empty db
        """
        return self.r.flushdb()

    def _trim(self, name, start=0, stop=-1):
        """
        Trim an existing list, it will contain only the specified range
        :param key:
        :param start:
        :param stop:
        :return:
        """
        return self.r.ltrim(name, start, stop)

    def _load_data(self,_json):
        """
        Loads json
        :param _json:
        :return:
        """
        result = json.loads(_json)
        return result


if __name__ == "__main__":
    qr = QueueRedis()
    qr.set("test", 15)
    qr.get("test")
    print(qr.get("test").decode("utf-8"))
    print(qr.exists("test"))
