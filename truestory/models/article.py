from truestory.models.base import BaseModel, ndb


class ArticleModel(ndb.Model):
    title = ndb.StringProperty()
    link = ndb.StringProperty()
    published = ndb.DateTimeProperty()
    summary = ndb.StringProperty()
    content = ndb.TextProperty(indexed=False)
    categories = ndb.StringProperty(repeated=True)
    authors = ndb.StringProperty(repeated=True)
    img = ndb.StringProperty()
    source = ndb.StringProperty()
