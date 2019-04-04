"""Web app (Flask) configuration settings."""


import base64
import hashlib

from truestory import settings


def get_secret_key():
    """Gets a constant secret key for sessions and cookies."""
    return hashlib.md5(
        base64.b64encode(settings.APP_NAME.encode(settings.ENCODING))
    ).digest()


class BaseConfig(object):

    """Common configuration."""

    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = False

    SECRET_KEY = get_secret_key()
    SSL_DISABLE = False

    DATASTORE_NAMESPACE = None  # Uses [default] implicitly.


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
