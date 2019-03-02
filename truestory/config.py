"""Web app (Flask) configuration settings."""


from truestory import settings, utils


class BaseConfig(object):

    """Common configuration."""

    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = False

    SECRET_KEY = utils.get_secret_key()
    SSL_DISABLE = False


class ProductionConfig(BaseConfig):

    """What is used in production (cloud deployment) runs."""


class DevelopmentConfig(BaseConfig):

    """Used while doing local development & debugging."""

    DEBUG = True
    PROPAGATE_EXCEPTIONS = True


class TestingConfig(BaseConfig):

    """Used when running tests."""

    TESTING = True
    WTF_CSRF_ENABLED = False


DefaultConfig = DevelopmentConfig if settings.DEBUG else ProductionConfig


config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DefaultConfig,
}
