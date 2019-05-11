"""Handles news article parsing."""


import logging
import os

import nltk
from flask import abort, current_app
from flask_json import FlaskJSON, as_json
from newspaper import Article as NewsArticle, ArticleException


NLP_ENABLED = bool(int(os.getenv("NLP_ENABLED", "1")))

if current_app:
    app_json = FlaskJSON(current_app)
if NLP_ENABLED:
    nltk.download("punkt")


def get_article(link):
    GAE_PRODUCTION = os.getenv("GAE_ENV", "").startswith("standard")
    if GAE_PRODUCTION:
        # This will not run in Cloud Functions (App Engine only).
        from truestory.functions.remote import get_remote_article
        return get_remote_article(link)

    article = NewsArticle(link)
    article.download()
    article.parse()
    if NLP_ENABLED:
        article.nlp()
    return article


@as_json
def parse_article(request):
    """Parses a given article `link` and returns its JSON details."""
    data = request.get_json() or request.args
    link = data.get("link")
    if not link:
        abort(400)

    try:
        article = get_article(link)
    except ArticleException as exc:
        logging.exception(exc)
        abort(404)

    details = {
        "news_article": {
            "text": article.text,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "top_image": article.top_image,
            "keywords": article.keywords,
        }
    }
    return details
