"""Tests articles and bias pairs."""


from .conftest import skip_missing_credentials


pytestmark = skip_missing_credentials


def test_bias_pair_save(bias_pair_ents):
    # Save the entities into DB.
    left, right, bias_pair = bias_pair_ents
    bias_pair.left = left.put()
    bias_pair.right = right.put()
    bias_pair.put()

    # Check data directly from the DB.
    new_bias_pair = bias_pair.myself
    assert left.get(new_bias_pair.left).title == "TrueStory 1"
    assert right.get(new_bias_pair.right).source_name == "BBC"

    # Remove them in reverse order.
    bias_pair.remove()
    left.remove()
    right.remove()
