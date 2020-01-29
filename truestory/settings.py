"""TrueStory default settings."""


import os


# Server environment and application settings.
GAE_DEBUG = not os.getenv("GAE_ENV", "").startswith("standard")
CONFIG = os.getenv("FLASK_CONFIG", "default")
DATASTORE_ENV = os.getenv("DATASTORE_ENV_YAML")
APP_NAME = "TrueStory"
PROJECT_ID = APP_NAME.lower()
LOCATION = "europe-west1"


class SERVER:
    HOST = "127.0.0.1"
    PORT = 8080
    GAE_DEBUG = GAE_DEBUG


# Miscellaneous.
TIMEOUT = 10  # seconds
ENCODING = "utf-8"
DEFAULT_MAIL = "hello@truestory.one"
PROJECT_NAME = PROJECT_ID

# Persistent logging (used while running outside Google Cloud).
LOGFILE = f"{PROJECT_NAME}.log"

# Article content display/retrieval settings on home, individual pages and API.
HOME_ARTICLE_MAX_SIZE = 256
FULL_ARTICLE_MAX_SIZE = 1024
AUTHORS_MAX_SIZE = 64
API_MAX_RELATED_ARTICLES = 3


# Misc.
class REDIS:
    """Redis client and wrappers settings."""
    HOST = os.getenv("REDIS_HOST", "localhost")
    PORT = os.getenv("REDIS_PORT", 6379)
    PASSWORD = os.getenv("REDIS_PASSWORD", None)
