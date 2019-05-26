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
    meta_func = lambda bias_pair: {
        "Bias score": int(bias_pair.score * 10),
        "Analysed at": views_base.format_date_filter(
            bias_pair.created_at, time=True
        ),
        # These are not rendered in the HTML (starting with underscore).
        "_score": bias_pair.score,
        "_created_at": bias_pair.created_at,
    }
    related_articles = ArticleModel.get_related_articles(
        main_article.key, meta_func=meta_func
    )
    related_articles = sorted(
        related_articles,
        key=lambda item: (item["meta"]["_score"], item["meta"]["_created_at"]),
        reverse=True
    )
    return render_template(
        "article.html",
        main_article=main_article,
        related_articles=related_articles,
    )
