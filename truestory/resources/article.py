"""API exposing article related data."""


from flask_restful import abort, request

from truestory import settings
from truestory.models import ArticleModel
from truestory.resources import base


class BaseArticleResource(base.BaseResource):

    """Base class for all article related resources."""

    URL_PREFIX = "/article"

    @staticmethod
    def _get_schemas():
        # Required due to circular import.
        from truestory.schemas.article import (
            article_schema, articles_schema
        )
        schemas = {
            "article": article_schema,
            "articles": articles_schema,
        }
        return schemas


class CounterArticleResource(BaseArticleResource):

    """Handles opposite articles."""

    ENDPOINT = "counter"

    def get(self):
        """Returns a list of opposite articles for the provided one."""
        link = request.args.get("link", "").strip()
        if not link:
            abort(400, message="Article 'link' not supplied.")

        article_query = ArticleModel.query(("link", "=", link))
        main_articles = ArticleModel.all(query=article_query, keys_only=True, limit=1)
        if not main_articles:
            abort(404, message="Article not found in the database.")

        main_article = main_articles[0]
        related_articles = ArticleModel.get_related_articles(main_article.key)
        articles = [
            article["article"] for article in related_articles
        ][:settings.API_MAX_RELATED_ARTICLES]
        main_article_url = self._make_response(
            "articles", [main_article]
        ).json["articles"][0]
        return self._make_response("articles", articles, main=main_article_url)


class DataArticleResource(BaseArticleResource):

    """Handles a full article."""

    ENDPOINT = "data"

    @classmethod
    def get_route(cls):
        return f"{super().get_route()}/<article_usafe>"

    def get(self, article_usafe):
        """Returns contents of an article."""
        try:
            article = ArticleModel.get(article_usafe)
        except Exception as exc:
            abort(404, message=str(exc))

        return self._make_response("article", article)
