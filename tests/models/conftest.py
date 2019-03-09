"""Setups and cleanups for Datastore related tests."""


import os

import pytest

from truestory.models import ArticleModel, BaseModel, BiasPairModel, ndb


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
def truestory_ent():
    """Returns our default model in order to test the DB for basic functionality."""
    return TrueStoryModel()


@pytest.fixture
def bias_pair_ents():
    """Returns a pair of two biased articles."""
    left = ArticleModel(
        source_name="BBC",
        link="http://truestory.one/article1",
        title="TrueStory 1",
        content="True Story 1",
    )
    right = ArticleModel(
        source_name="BBC",
        link="http://truestory.one/article2",
        title="TrueStory 2",
        content="True Story 2",
    )
    return left, right, BiasPairModel(left=left.key, right=right.key)


CLEANUP_MODELS = [
    ArticleModel,
    BiasPairModel,
    TrueStoryModel,
]


@pytest.fixture(autouse=True, scope="session")
def datastore_cleanup():
    yield
    if not NO_CREDENTIALS:
        total = []
        for Model in CLEANUP_MODELS:
            items = Model.all(keys_only=True)
            total.extend(items)
        BaseModel.remove_multi([item.key for item in total])
