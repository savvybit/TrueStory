"""Web app (Flask) configuration settings."""


from truestory import settings, utils


class BaseConfig(object):

    """Common configuration."""

    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = False

    SECRET_KEY = utils.get_secret_key()
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
