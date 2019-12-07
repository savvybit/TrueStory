"""Miscellaneous."""


import redis

from truestory.settings import REDIS


def get_redis_client():
    redis_client = redis.StrictRedis(
        host=REDIS.HOST, port=REDIS.PORT, password=REDIS.PASSWORD
    )
    redis_client.ping()
    return redis_client
