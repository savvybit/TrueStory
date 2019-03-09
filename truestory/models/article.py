"""Article related models."""


import functools

from truestory.models.base import BaseModel, ndb


class ArticleModel(BaseModel):

    """Extracted and processed article."""

    source_name = ndb.StringProperty(required=True)
    link = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True, indexed=False)
    summary = ndb.StringProperty()
    authors = ndb.StringProperty(repeated=True)
    published = ndb.DateTimeProperty()
    image = ndb.StringProperty()
    keywords = ndb.StringProperty(repeated=True)


class BiasPairModel(BaseModel):

    """A pair of two biased articles."""

    left = ndb.KeyProperty(kind=ArticleModel, required=True)
    right = ndb.KeyProperty(kind=ArticleModel, required=True)
    score = ndb.FloatProperty()
    published = ndb.DateTimeProperty()  # cannot save datetime computed properties

    def _max_date(self):
        """The newest article establishes the date of the entire pair."""
        dates = self.get(self.left).published, self.get(self.right).published
        if all(dates):
            return max(dates)
        return dates[0] or dates[1]

    def put(self):
        self.published = self._max_date()
        return super().put()

    @functools.partial(ndb.ComputedProperty, repeated=True)
    def keywords(self):
        """Combines all the keywords into an unique list."""
        left_kwds, right_kwds = map(
            lambda key: set(self.get(key).keywords or []), [self.left, self.right]
        )
        return list(left_kwds | right_kwds)
