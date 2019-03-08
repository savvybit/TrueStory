"""Setups and cleanups for Datastore related tests."""


import os

import pytest

from truestory.models import BaseModel, ndb


NO_CREDENTIALS = not bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

skip_missing_credentials = pytest.mark.skipif(
    NO_CREDENTIALS, reason="missing Datastore credentials"
)


class TrueStoryModel(BaseModel):

    bool_prop = ndb.BooleanProperty(default=False)
    str_prop = ndb.StringProperty(
        default="str_prop", choices=["str_prop", "string_prop"]
    )
    txt_prop = ndb.TextProperty(indexed=False)
    list_prop = ndb.IntegerProperty(repeated=True)
    auto_prop = ndb.ComputedProperty(lambda self: sum(self.list_prop))


@pytest.fixture
def truestory_model():
    """Returns our default model in order to test the DB for basic functionality."""
    return TrueStoryModel()


@pytest.fixture(autouse=True, scope="session")
def datastore_cleanup():
    yield
    if not NO_CREDENTIALS:
        items = TrueStoryModel.all(keys_only=True)
        TrueStoryModel.remove_multi([item.key for item in items])
