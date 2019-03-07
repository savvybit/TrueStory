"""Article related models."""


from truestory.models.base import BaseModel, ndb


class ArticleModel(BaseModel):

    """Extracted and processed article."""

    source = ndb.StringProperty()
    link = ndb.StringProperty()
    title = ndb.StringProperty()
    content = ndb.TextProperty(indexed=False)
    summary = ndb.StringProperty()
    authors = ndb.StringProperty(repeated=True)
    published = ndb.DateTimeProperty()
    img = ndb.StringProperty()
    categories = ndb.StringProperty(repeated=True)
