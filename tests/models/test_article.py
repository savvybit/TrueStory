"""Tests articles and bias pairs."""


from truestory.models import ArticleModel, BiasPairModel
from .conftest import skip_no_datastore


pytestmark = skip_no_datastore


def test_bias_pair_save(bias_pair_ents):
    # Save the entities into DB.
    left, right, bias_pair = bias_pair_ents
    bias_pair.left = left.put()
    bias_pair.right = right.put()
    bias_pair.put()

    # Check data directly from the DB (not using the local entity).
    new_bias_pair = bias_pair.myself
    assert new_bias_pair.left.get().title == "TrueStory 1"
    assert new_bias_pair.right.get().source_name == "BBC"

    # Remove them in reverse order.
    bias_pair.remove()
    left.remove()
    right.remove()


def test_related_articles(bias_pair_ents):
    left, right, bias_pair = bias_pair_ents
    bias_pair.left = left.put()
    bias_pair.right = right.put()
    bias_pair.put()

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
