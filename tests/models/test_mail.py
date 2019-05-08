"""Tests mail saving and retrieval from the Datastore."""


from .conftest import skip_no_datastore


pytestmark = skip_no_datastore


def test_subscriber_save_get(subscriber_ent):
    subscriber_key = subscriber_ent.put()
    hash1 = subscriber_key.get().hashsum
    hash2 = subscriber_ent.myself.hashsum
    assert hash1 == hash2
    assert subscriber_ent.subscribed is True
