"""TrueStory default settings."""


import os
from pathlib import Path


# Server environment and application settings.
DEBUG = not os.getenv("GAE_ENV", "").startswith("standard")
CONFIG = os.getenv("FLASK_CONFIG", "default")
APP_NAME = "TrueStory"
PROJECT_ID = APP_NAME.lower()

# Miscellaneous.
TIMEOUT = 10  # seconds
ENCODING = "utf-8"

# Paths.
PROJECT_DIR = Path(__file__).parent.parent
WORK_DIR = Path(f"~/Work/{APP_NAME}").expanduser()

# Persistent logging (used while running outside Google Cloud).
LOGFILE = "truestory.log"

# Article content display settings on home and individual page.
HOME_ARTICLE_MAX_SIZE = 256
FULL_ARTICLE_MAX_SIZE = 1024
