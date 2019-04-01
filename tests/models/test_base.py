"""Tests base utilities used in Datastore interactions."""


from .conftest import TrueStoryModel, skip_missing_credentials


pytestmark = skip_missing_credentials


def test_model_no_save(truestory_ent):
    # Check direct assigned properties.
    assert not truestory_ent.bool_prop
    assert truestory_ent.str_prop == "str_prop"
    assert truestory_ent.txt_prop is None
    assert truestory_ent.auto_prop == 0

    # Check base model utilities.
    assert truestory_ent.model_name() == "TrueStory"
    assert truestory_ent.normalize(truestory_ent.txt_prop) == "N/A"
    assert not truestory_ent.exists


def test_model_save_delete(truestory_ent):
    truestory_ent.put()
    assert truestory_ent.exists

    # Test local vs. remote diffs.
    truestory_ent.bool_prop = True
    assert truestory_ent.bool_prop != truestory_ent.myself.bool_prop

    # Test urlsafe generation and retrieval.
    truestory_ent.bool_prop = True
    truestory_ent.put()
    assert truestory_ent.get(truestory_ent.urlsafe).bool_prop

    truestory_ent.remove()
    assert not truestory_ent.exists


def test_model_query(truestory_ent):
    # The sum of the numbers in the list should be equal to `total`.
    nr = 4
    total = nr * (nr + 1) // 2
    truestory_ent.list_prop = list(range(nr + 1))
    truestory_ent.put()

    # Checking each of them for the edge case when the DB is dirty (parallel tests).
    entities = TrueStoryModel.all()
    flags = [entity.auto_prop == total for entity in entities]
    assert any(flags)

    # Same as above, but this time using a custom query.
    query = TrueStoryModel.query()
    query.add_filter("auto_prop", "=", total)
    assert list(query.fetch())  # At least one item in the list.

    # Explicit cleanup (even if is not required).
    truestory_ent.remove()
