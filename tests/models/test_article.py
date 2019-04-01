"""Tests articles and bias pairs."""


from .conftest import skip_missing_credentials


pytestmark = skip_missing_credentials


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
