"""Miscellaneous."""


import functools
import json
import pathlib

import addict
import redis
import toml

from truestory.settings import REDIS


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


def get_from_file(stream_or_path, is_json=True):
    """Get deserialized content within a JSON or Toml file.

    Args:
        stream_or_path (str/object): Path to file or open stream of data.
        is_json (bool): True if this is JSON content, False if is Toml.

    Returns:
        addict.Dict: Dictionary-like object containing the read data.
    """
    if not hasattr(stream_or_path, "read"):
        with open(str(stream_or_path)) as stream:
            return get_from_file(stream, is_json=is_json)

    if is_json:
        message_dict = json.load(stream_or_path)
    else:
        message_dict = toml.load(stream_or_path)
    return addict.Dict(message_dict)


# Shortcuts for getting relative file content inside local "data" directory.
_get_content = lambda name, current_path, *, dir_name, is_json: get_from_file(
    pathlib.Path(current_path).resolve().parent / dir_name / name, is_json=is_json
)
get_toml_data = functools.partial(_get_content, dir_name="data", is_json=False)
