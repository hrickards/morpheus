import redis
import cPickle as pickle

class Cache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.StrictRedis(host=host, port=port, db=db)

    def get(self, key):
        raw = self.r.get(key)
        if raw == None: return None
        return pickle.loads(raw)

    def set(self, key, obj):
        return self.r.set(key, pickle.dumps(obj))
