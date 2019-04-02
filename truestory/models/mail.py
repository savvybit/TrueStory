"""E-mails storage."""


import hashlib

from truestory import settings
from truestory.models.base import BaseModel, ndb


class MailModel(BaseModel):

    """Subscriber e-mail got from the landing page."""

    mail = ndb.StringProperty(required=True)

    @ndb.ComputedProperty
    def hashsum(self):
        string = f"{self.mail}_{self.created_at.isoformat()}"
        return hashlib.md5(string.encode(settings.ENCODING)).hexdigest()
