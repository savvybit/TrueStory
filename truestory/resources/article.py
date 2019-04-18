"""API exposing article related data."""


from truestory.models import ArticleModel, BiasPairModel
from truestory.resources import base


class BaseArticleResource(base.BaseResource):

    """Base class for all article related resources."""

    URL_PREFIX = "/article"

    @staticmethod
    def _get_schemas(which):
        # Required due to circular import.
        from truestory.schemas.article import article_schema, articles_schema
        schemas = {
            "article": article_schema,
            "articles": articles_schema,
        }
        return schemas[which]


class CounterArticleResource(BaseArticleResource):

    """Handles opposite articles."""

    ENDPOINT = "counter"

    def get(self):
        """Returns a list of opposite articles for the provided one."""
        articles = ArticleModel.all(limit=3)
        articles_schema = self._get_schemas("articles")
        return articles_schema.jsonify(articles)


class DataArticleResource(BaseArticleResource):

    """Handles a full article."""

    ENDPOINT = "data"

    @classmethod
    def get_route(cls):
        return f"{super().get_route()}/<article_usafe>"

    def get(self, article_usafe):
        """Returns contents of an article."""
        article = ArticleModel.get(article_usafe)
        article_schema = self._get_schemas("article")
        return article_schema.jsonify(article)
