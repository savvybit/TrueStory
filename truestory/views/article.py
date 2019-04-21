"""Handles individual '/article' page."""


from flask import render_template

from truestory import app
from truestory.models.article import ArticleModel
from truestory.views import base as views_base


@app.route("/article/<article_usafe>")
@views_base.require_auth
def article_view(article_usafe):
    """Displays article details and its opposed ones."""
    main_article = ArticleModel.get(article_usafe)
    meta_func = lambda pair: {
        "Bias score": int(pair.score or 0),
        "Analysed at": views_base.format_date_filter(
            pair.created_at, time=True
        ),
        # These are not rendered in the HTML (starting with underscore).
        "_score": pair.score,
        "_created_at": pair.created_at,
    }
    related_articles = ArticleModel.get_related_articles(
        main_article.key, meta_func=meta_func
    )
    related_articles.sort(
        key=lambda item: (item[1]["_score"], item[1]["_created_at"]), reverse=True
    )
    return render_template(
        "article.html",
        main_article=main_article,
        related_articles=related_articles,
    )
