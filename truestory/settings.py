"""TrueStory default settings."""


import os


# Server environment and application settings.
DEBUG = not os.getenv("GAE_ENV", "").startswith("standard")
CONFIG = os.getenv("FLASK_CONFIG", "default")
APP_NAME = "TrueStory"
PROJECT_ID = APP_NAME.lower()

# Miscellaneous.
TIMEOUT = 10  # seconds
ENCODING = "utf-8"
PROJECT_DIR = os.path.normpath(
    # Project directory (package parent).
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)

# Persistent logging (used while running outside Google Cloud).
LOGFILE = "truestory.log"

