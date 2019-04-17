"""API exposing article related data."""


from truestory.resources import base


class BaseArticleResource(base.BaseResource):

    """Base class for all article related resources."""

    URL_PREFIX = "/article"


class CounterArticleResource(BaseArticleResource):

    """Handles opposite articles."""

    ENDPOINT = "counter"

    def get(self):
        """Returns a list of opposite articles for the provided one."""
        return []
