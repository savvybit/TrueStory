"""Tests articles and bias pairs."""


from truestory.models import ArticleModel, BiasPairModel
from truestory.tasks.article import _clean_articles

from .conftest import skip_no_datastore, wait_exists


pytestmark = skip_no_datastore


def test_bias_pair_save(bias_pair_ents):
    left, right, bias_pair = bias_pair_ents

    # Check data directly from the DB (not using the local entity).
    new_bias_pair = bias_pair.myself
    assert new_bias_pair.left.get().title.startswith("TrueStory")
    assert new_bias_pair.right.get().source_name == "BBC"

    # Remove them in reverse order.
    bias_pair.remove()
    left.remove()
    right.remove()


def test_related_articles(bias_pair_ents):
    left, right, bias_pair = bias_pair_ents

    rev_bias_pair = BiasPairModel(left=bias_pair.right, right=bias_pair.left)
    rev_bias_pair.put()

    articles = ArticleModel.get_related_articles(left.key)
    assert len(articles) == 1, "duplicate articles"

    article_date = list(articles)[0]["created_at"].replace(tzinfo=None)
    assert article_date == max(
        bias.created_at for bias in (bias_pair, rev_bias_pair)
    ), "outdated bias pair"

    for entity in (rev_bias_pair, bias_pair, left, right):
        entity.remove()


def test_cleanup(bias_pair_ents):
    _clean_articles()
    any_alive = any(ent.exists for ent in bias_pair_ents)
    assert not any_alive, "entities aren't cleaned up"


def test_duplicate(left_article_ent, right_article_ent):
    left_article_ent.put()
    wait_exists(left_article_ent)

    right_article_ent.link = left_article_ent.link
    right_article_ent.put()
    assert left_article_ent.myself.title == right_article_ent.title, "original not updated"
    assert not right_article_ent.exists, "saved duplicate"
