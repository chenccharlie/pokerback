import pickle
import redis
from functools import lru_cache

from django.conf import settings


@lru_cache(3)
def get_redis():
    return RedisClient()


class RedisClient:
    def __init__(self, host=settings.REDIS_HOST):
        self.redis_client = redis.StrictRedis(host)

    def set(self, key, val):
        if isinstance(val, dict):
            return self.redis_client.set(key, pickle.dumps(val))
        else:
            return self.redis_client.set(key, val)

    def get(self, key):
        try:
            return pickle.loads(self.redis_client.get(key))
        except Exception:
            return self.redis_client.get(key)

    def update_dict(self, key, dict_vals):
        cur = self.get(key)
        if not isinstance(cur, dict):
            raise Exception("Value being updated is not a dict")
        cur.update(dict_vals)
        self.set(key, cur)