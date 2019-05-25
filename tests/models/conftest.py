"""Setups and cleanups procedures for Datastore related tests."""


import datetime
import os
import random
import time

import pytest
from truestory import settings
from truestory.models import (
    ArticleModel, BaseModel, BiasPairModel, SubscriberModel, ndb,
)


NO_CREDENTIALS = not bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

skip_no_datastore = pytest.mark.skipif(
    not settings.DATASTORE_ENV and NO_CREDENTIALS,
    reason="can't connect to local or remote Datastore"
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


def _article_ent(label):
    # Expired article.
    published = datetime.datetime.utcnow() - datetime.timedelta(days=3)
    article = ArticleModel(
        source_name="BBC",
        link=f"https://truestory.one/article{label}",
        title=f"TrueStory {label}",
        content=f"True Story {label}",
        published=published,
    )
    return article


@pytest.fixture
def left_article_ent():
    return _article_ent(random.randint(1, 100))


@pytest.fixture
def right_article_ent():
    return _article_ent(random.randint(101, 200))


@pytest.fixture
def bias_pair_ents(left_article_ent, right_article_ent):
    """Returns a pair of two biased articles."""
    bias_pair = BiasPairModel(
        left=left_article_ent.put(), right=right_article_ent.put()
    )
    bias_pair.put()
    return left_article_ent, right_article_ent, bias_pair


@pytest.fixture
def subscriber_ent():
    """Returns a mail object with a default mail string."""
    return SubscriberModel(mail="test@example.com")


CLEANUP_MODELS = [
    ArticleModel,
    BiasPairModel,
    SubscriberModel,
    TrueStoryModel,
]


@pytest.fixture(autouse=True, scope="session")
def datastore_cleanup():
    yield
    if not skip_no_datastore.args[0]:
        all_entities = []
        for Model in CLEANUP_MODELS:
            entities = Model.all(keys_only=True)
            all_entities.extend(entities)
        BaseModel.remove_multi([entity.key for entity in all_entities])


def wait_exists(entity):
    while not entity.exists:
        time.sleep(0.1)
