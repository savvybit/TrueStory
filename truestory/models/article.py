from truestory.models.base import BaseModel, ndb


class ArticleModel(ndb.Model):
    title = ndb.StringProperty()
    link = ndb.StringProperty()
    id = ndb.StringProperty()
    published = ndb.DateTimeProperty()
    updated = ndb.DateTimeProperty()
    summary = ndb.StringProperty()
    language = ndb.StringProperty()
    type = ndb.StringProperty()
    content = ndb.TextProperty()
    categories = ndb.StringProperty(repeated=True)
