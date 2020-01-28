"""Web app (Flask) configuration settings."""


import base64
import hashlib
import logging
import os
import requests

import yaml

from truestory import misc, settings


def _get_secret_key():
    """Gets a constant secret key for sessions and cookies."""
    return hashlib.md5(
        base64.b64encode(settings.APP_NAME.encode(settings.ENCODING))
    ).digest()


def init_datastore_emulator():
    path = settings.DATASTORE_ENV
    if not path:
        return

    logging.info("Datastore emulator detected, initializing environment.")
    if not os.path.isfile(path):
        raise Exception("Datastore emulator was never ran")
    with open(path) as stream:
        env_dict = yaml.load(stream, Loader=yaml.Loader)
    os.environ.update(env_dict)

    try:
        requests.get(os.getenv("DATASTORE_HOST")).raise_for_status()
    except requests.exceptions.ConnectionError:
        raise Exception("Datastore emulator is not started")


class BaseConfig(object):

    """Common configuration."""

    _CONFIG = misc.get_toml_data("config.toml", __file__)

    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = False

    SECRET_KEY = _get_secret_key()
    SSL_DISABLE = False

    DATASTORE_NAMESPACE = None  # Uses [default] implicitly.

    RATELIMIT_DEFAULT = _CONFIG.rate_limiter.default
    RATELIMIT_STORAGE_URL = misc.get_redis_url()
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_IN_MEMORY_FALLBACK = RATELIMIT_DEFAULT
    RATELIMIT_KEY_PREFIX = "truestory"


class ProductionConfig(BaseConfig):

    """What is used in production (cloud deployment) runs."""

    DATASTORE_NAMESPACE = "production"


class DevelopmentConfig(BaseConfig):

    """Used while doing local development & debugging."""

    DEBUG = True
    PROPAGATE_EXCEPTIONS = True

    DATASTORE_NAMESPACE = "development"


class TestingConfig(BaseConfig):

    """Used when running tests."""

    TESTING = True
    WTF_CSRF_ENABLED = False

    DATASTORE_NAMESPACE = "testing"


DefaultConfig = DevelopmentConfig if settings.DEBUG else ProductionConfig
config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DefaultConfig,
}
