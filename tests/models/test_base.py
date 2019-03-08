"""Tests base utilities used in Datastore interactions."""


from .conftest import TrueStoryModel, skip_missing_credentials


pytestmark = skip_missing_credentials


def test_model_no_save(truestory_model):
    # Check basic property data.
    assert not truestory_model.bool_prop
    assert truestory_model.str_prop == "str_prop"
    assert truestory_model.txt_prop is None
    assert truestory_model.auto_prop == 0

    # Check utilities.
    assert truestory_model.model_name() == "TrueStory"
    assert truestory_model.normalize(truestory_model.txt_prop) == "N/A"
    assert not truestory_model.exists


def test_model_save_delete(truestory_model):
    # Test saving.
    truestory_model.put()
    assert truestory_model.exists

    # Test local vs. remote diffs.
    truestory_model.bool_prop = True
    assert truestory_model.bool_prop != truestory_model.myself.bool_prop

    # Test urlsafe retrieval.
    truestory_model.bool_prop = True
    truestory_model.put()
    assert truestory_model.get(truestory_model.urlsafe).bool_prop

    # Test removal.
    truestory_model.remove()
    assert not truestory_model.exists


def test_model_query(truestory_model):
    # Save it with some data first in order to be able to query something relevant.
    nr = 4
    total = nr * (nr + 1) // 2
    truestory_model.list_prop = list(range(nr + 1))
    truestory_model.put()

    # Check if the computed property correctly sums up the previously set numbers.
    items = TrueStoryModel.all()
    # We try with all of them for the edge case where the DB is dirty.
    flags = [item.auto_prop == total for item in items]
    assert any(flags)

    # Test with custom query this time.
    query = TrueStoryModel.query()
    query.add_filter("auto_prop", "=", total)
    assert list(query.fetch())  # At least one item in the list.

    # Explicit cleanup (even if not required).
    truestory_model.remove()
