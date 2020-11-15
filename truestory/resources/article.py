"""API exposing article related data."""


import hashlib
import logging
import operator

import addict
from flask_restful import abort, request
from werkzeug.exceptions import HTTPException

from truestory import app, auth, get_remote_address, limiter, settings
from truestory.crawlers import RssCrawler
from truestory.crawlers.common import strip_article_link
from truestory.models import ArticleModel
from truestory.models.base import key_to_urlsafe
from truestory.resources import base


# Lazily loaded.
pair_article = None


def _pair_article(article_usafe):
    global pair_article
    if not pair_article:
        from truestory.tasks import pair_article
    return pair_article(article_usafe)


def _extract_article(link, site, site_info):
    feed_entry = addict.Dict({
        "link": link,
    })
    target = addict.Dict({
        "source_name": site_info["source"],
        "site": site,
        "side": ArticleModel.SIDE_MAPPING[site_info["side"]],
    })
    logging.info(
        "Crawling new article from %s: %s...", target.source_name, feed_entry.link
    )
    return RssCrawler.extract_article(feed_entry, target)


def _get_limit_conf():
    token = base.get_auth_token()
    limiter_conf = app.config["CONFIG"].rate_limiter
    for limit_conf in limiter_conf.emails:
        conf_token = auth.compute_token(limit_conf.email)
        if conf_token == token:
            limit_conf.token = token
            return limit_conf

    raise Exception("authorized token without rate limit set")


def _get_article_limit_func():
    limit_conf = _get_limit_conf()
    return limit_conf.limit


def _token_key_func():
    limit_conf = _get_limit_conf()
    token_hash = hashlib.md5(limit_conf.token.encode(settings.ENCODING)).hexdigest()
    ip_addr = f":{get_remote_address()}" if limit_conf.share else ""
    return f"{token_hash}{ip_addr}"


def _exempt_when_abort():
    try:
        request.articles_pair = CounterArticleResource.get_related_articles()
    except HTTPException as exc:
        logging.debug("Couldn't get related articles due to: %s", exc)
        request.exception = exc
        return True
    else:
        request.exception = None

    return False


class BaseArticleResource(base.DatastoreMixin, base.BaseResource):

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

    """Handles GETs of opposite articles."""

    ENDPOINT = "counter"

    if not app.debug:
        decorators = [
            limiter.limit(
                _get_article_limit_func,
                key_func=_token_key_func,
                exempt_when=_exempt_when_abort,
                per_method=True,
                methods=["GET"],
                override_defaults=False
            ),
        ]

    @staticmethod
    def get_related_articles():
        data = request.get_json(silent=True) or request.args
        link = data.get("link", "").strip()
        if not link:
            abort(400, message="Article 'link' not supplied.")

        link = strip_article_link(link)
        article_query = ArticleModel.query(("link", "=", link))
        main_articles = ArticleModel.all(query=article_query, keys_only=True, limit=1)
        if not main_articles:
            abort(404, message="Article not found in the database.")

        main_article = main_articles[0]
        related_articles = ArticleModel.get_related_articles(main_article.key)
        if not related_articles:
            abort(404, message="No related articles found.")

        return main_article, related_articles

    def get(self):
        """Returns a list of opposite articles for the provided one."""
        if app.debug:
            main_article, related_articles = self.get_related_articles()
        else:
            if request.exception:
                raise request.exception
            main_article, related_articles = request.articles_pair

        articles = []
        unique_sources = set()
        for article in sorted(
                related_articles, key=operator.itemgetter("score"), reverse=True
        ):
            article = article["article"]
            if article.source_name in unique_sources:
                continue
            else:
                unique_sources.add(article.source_name)
            articles.append(article)
            if len(articles) >= settings.API_MAX_RELATED_ARTICLES:
                break

        main_article_url = self._make_response(
            "articles", [main_article]
        ).json["articles"][0]
        return self._make_response("articles", articles, main=main_article_url)

    def post(self):
        data = request.get_json()
        link = data.get("link", "").strip() if data else None
        if not link:
            abort(400, message="Article 'link' not supplied.")

        link = strip_article_link(link)
        try:
            site, site_info = ArticleModel.get_site_info(link)
        except Exception as exc:
            abort(403, message=base.exc_to_str(exc))

        article = _extract_article(link, site, site_info)
        article_key = article.put()
        article_usafe = key_to_urlsafe(article_key)
        try:
            _pair_article(article_usafe)
        except Exception as exc:
            logging.exception(
                "Couldn't pair article with urlsafe '%s' due to: %s",
                article_usafe,
                exc
            )
        return self._make_response("article", article)


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
            abort(404, message=base.exc_to_str(exc))

        return self._make_response("article", article)
