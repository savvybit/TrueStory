"""Gather here all RSS related models."""


from truestory.models.base import BaseModel, ndb


class RssTargetModel(BaseModel):

    """RSS feed source used by the RSS crawler."""

    link = ndb.StringProperty()
    source_name = ndb.StringProperty()
    last_modified = ndb.DateTimeProperty()
    etag = ndb.StringProperty()
    auth_required = ndb.BooleanProperty(default=False)
    gone = ndb.BooleanProperty(default=False)

    def checkpoint(self, modified, etag):
        """Called after each successful crawl in order to know from where to start
        next time.
        """
        self.last_modified = modified
        self.etag = etag
        self.put()

    def has_gone(self):
        """This feed is dead, do not crawl it again."""
        self.gone = True
        self.put()

    def needs_auth(self):
        """Mark this feed with required authentication in order to skip it if auth is
        not supported.
        """
        self.auth_required = True
        self.put()

    def moved_to(self, link):
        """Saves the new address when it permanently moves."""
        self.link = link
        self.put()
