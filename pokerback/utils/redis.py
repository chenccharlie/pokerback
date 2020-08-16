import pickle
import redis
import redis_lock
from functools import lru_cache

from django.conf import settings


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

    def get_lock(self, key, blocking=True):
        lock = redis_lock.Lock(self.redis_client, key)
        if lock.acquire(blocking=blocking):
            return lock
        else:
            raise RedisLockError()


@lru_cache(3)
def get_redis():
    return RedisClient()


class RedisLockError(Exception):
    pass


class RedisLock:
    def __init__(self, lock_key, redis_client=get_redis()):
        self.lock_key = lock_key
        self.redis_client = redis_client
        self.lock = None

    def __enter__(self):
        self.lock = self.redis_client.get_lock(self.lock_key)

    def __exit__(self, type, value, traceback):
        self.lock.release()
