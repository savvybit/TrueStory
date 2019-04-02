"""E-mails storage."""


import datetime
import hashlib

from truestory import settings
from truestory.models.base import BaseModel, ndb


class MailModel(BaseModel):

    """Subscriber e-mail got from the landing page."""

    mail = ndb.StringProperty(required=True)
    hashsum = ndb.StringProperty(required=True)

    def put(self):
        date = datetime.datetime.utcnow()
        string = f"{self.mail}_{date.isoformat()}"
        self.hashsum = hashlib.md5(string.encode(settings.ENCODING)).hexdigest()
        return super().put()
