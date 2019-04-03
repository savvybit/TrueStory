"""Tests mail saving and retrieval from the Datastore."""


from .conftest import skip_missing_credentials


pytestmark = skip_missing_credentials


def test_subscriber_save_get(subscriber_ent):
    mail_key = subscriber_ent.put()
    hash1 = mail_key.get().hashsum
    hash2 = subscriber_ent.myself.hashsum
    assert hash1 == hash2
    assert subscriber_ent.subscribed is True
