"""Web app (Flask) configuration settings."""


from truestory import settings, utils


class BaseConfig(object):

    """Common configuration."""

    DEBUG = False
    TESTING = False

    SECRET_KEY = utils.get_secret_key()
    SSL_DISABLE = False

    PROPAGATE_EXCEPTIONS = False


class ProductionConfig(BaseConfig):

    """What is used in production and normal runs."""


class DevelopmentConfig(BaseConfig):

    """Used while doing development & debugging."""

    DEBUG = True


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
