"""Various general purpose utilities."""


import base64
import hashlib
import os

from truestory import settings


def read(fpath):
    """Reads the content of a file relative to project."""
    with open(os.path.join(settings.PROJECT_DIR, fpath)) as stream:
        return stream.read()


def get_secret_key():
    """Gets a constant secret key for sessions and cookies."""
    return hashlib.md5(base64.b64encode(settings.APP_NAME.encode())).hexdigest()

