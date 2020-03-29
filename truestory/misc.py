"""Miscellaneous."""


import urllib.request as urlopen

import redis
import requests

from truestory.settings import REDIS, USER_AGENT


HEADERS = {
    "User-Agent": USER_AGENT,
}


def get_redis_client():
    redis_client = redis.StrictRedis(
        host=REDIS.HOST, port=REDIS.PORT, password=REDIS.PASSWORD
    )
    redis_client.ping()
    return redis_client


def get_redis_url():
    if REDIS.PASSWORD:
        auth = f":{REDIS.PASSWORD}@"
    else:
        auth = ""
    return f"redis://{auth}{REDIS.HOST}:{REDIS.PORT}"


def get_url_opener():
    opener = urlopen.build_opener()
    opener.addheaders = list(HEADERS.items())
    return opener


class RequestsSession(requests.Session):

    def __init__(self):
        super().__init__()
        self.headers.update(HEADERS)
