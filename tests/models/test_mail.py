"""Tests mail saving and retrieval from the Datastore."""


from .conftest import skip_missing_credentials


pytestmark = skip_missing_credentials


def test_mail_save_get(mail_ent):
    mail_key = mail_ent.put()
    hash1 = mail_key.get().hashsum
    hash2 = mail_ent.myself.hashsum
    assert hash1 == hash2
