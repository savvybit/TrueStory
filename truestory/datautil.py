"""Utilities playing with data files."""


import csv
import functools
import io
import json

import addict
import toml
import pkg_resources

from truestory import settings


LOADERS = {
    "json": json.load,
    "toml": toml.load,
    "csv": csv.DictReader,
}


def get_string(path):
    """Returns string content from `path` file."""
    content = pkg_resources.resource_string(settings.PROJECT_NAME, path)
    return content.decode(settings.ENCODING).strip()


def get_stream(path, binary=True):
    """Returns a file-like object for the one pointed by `path`."""
    stream = pkg_resources.resource_stream(settings.PROJECT_NAME, path)
    if not binary:
        stream = io.TextIOWrapper(stream)
    return stream


def get_structured(path, *, file_type):
    """Get deserialized content within a JSON or Toml file.

    Args:
        path (str): Path to file on disk.
        file_type (str): Choose between json/toml/csv.

    Returns:
        addict.Dict: Dictionary-like object containing the read data.
    """
    assert file_type in LOADERS, "invalid file type for loading content"
    stream = get_stream(path, binary=file_type in ("json",))
    message_dict = LOADERS[file_type](stream)
    if file_type == "csv":
        message_dict = {"reader": message_dict}
    return addict.Dict(message_dict)


get_json_data = functools.partial(get_structured, file_type="json")
get_toml_data = functools.partial(get_structured, file_type="toml")
get_csv_data = functools.partial(get_structured, file_type="csv")
