"""TrueStory default settings."""


import os


# Server environment and application settings.
DEBUG = not os.getenv("GAE_ENV", "").startswith("standard")
CONFIG = os.getenv("FLASK_CONFIG", "default")
DATASTORE_ENV = os.getenv("DATASTORE_ENV_YAML")
APP_NAME = "TrueStory"
PROJECT_ID = APP_NAME.lower()

# Miscellaneous.
TIMEOUT = 10  # seconds
ENCODING = "utf-8"
DEFAULT_MAIL = "hello@truestory.one"

# Persistent logging (used while running outside Google Cloud).
LOGFILE = "truestory.log"

# Article content display settings on home and individual pages.
HOME_ARTICLE_MAX_SIZE = 256
FULL_ARTICLE_MAX_SIZE = 1024
