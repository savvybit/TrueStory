"""Utilities playing with data files."""


import pkg_resources

from truestory import settings


def get_string(path):
    """Returns string content from `path` file."""
    content = pkg_resources.resource_string(settings.PROJECT_NAME, path)
    return content.decode(settings.ENCODING).strip()


def get_stream(path):
    """Returns a file-like object for the one pointed by `path`."""
    return pkg_resources.resource_stream(settings.PROJECT_NAME, path)
