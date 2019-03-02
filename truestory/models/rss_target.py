from truestory.models.base import BaseModel, ndb


class RssTargetModel(ndb.Model):
    link = ndb.StringProperty()
    etag = ndb.StringProperty()
    last_modified = ndb.DateTimeProperty()
    auth_required = ndb.BooleanProperty()
