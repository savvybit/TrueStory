"""Tests base utilities used in Datastore interactions."""


from .conftest import TrueStoryModel, skip_missing_credentials


pytestmark = skip_missing_credentials


def test_model_no_save(truestory_ent):
    # Check basic property data.
    assert not truestory_ent.bool_prop
    assert truestory_ent.str_prop == "str_prop"
    assert truestory_ent.txt_prop is None
    assert truestory_ent.auto_prop == 0

    # Check utilities.
    assert truestory_ent.model_name() == "TrueStory"
    assert truestory_ent.normalize(truestory_ent.txt_prop) == "N/A"
    assert not truestory_ent.exists


def test_model_save_delete(truestory_ent):
    # Test saving.
    truestory_ent.put()
    assert truestory_ent.exists

    # Test local vs. remote diffs.
    truestory_ent.bool_prop = True
    assert truestory_ent.bool_prop != truestory_ent.myself.bool_prop

    # Test urlsafe retrieval.
    truestory_ent.bool_prop = True
    truestory_ent.put()
    assert truestory_ent.get(truestory_ent.urlsafe).bool_prop

    # Test removal.
    truestory_ent.remove()
    assert not truestory_ent.exists


def test_model_query(truestory_ent):
    # Save it with some data first in order to be able to query something relevant.
    nr = 4
    total = nr * (nr + 1) // 2
    truestory_ent.list_prop = list(range(nr + 1))
    truestory_ent.put()

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
    truestory_ent.remove()
