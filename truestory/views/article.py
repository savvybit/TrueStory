"""Handles individual '/article' page."""


from flask import render_template

from truestory import app
from truestory.models.article import ArticleModel, BiasPairModel
from truestory.views import base as views_base


@app.route("/article/<article_usafe>")
def article_view(article_usafe):
    """Displays article details and its opposed ones."""
    main_article = ArticleModel.get(article_usafe)
    related_articles = []
    seen_articles = {}

    complementary = {"left": "right", "right": "left"}
    for side in complementary:
        query = BiasPairModel.query()
        query.add_filter(side, "=", main_article.key)
        pairs = list(query.fetch())

        for pair in pairs:
            article = getattr(pair, complementary[side]).get()

            # Keep unique related articles only (choose the newest one if duplicates
            # are found).
            usafe = article.urlsafe
            seen_date = seen_articles.get(usafe)
            if seen_date and pair.created_at <= seen_date:
                continue

            meta = {
                "Bias score": int(pair.score),
                "Created at": views_base.format_date_filter(
                    pair.created_at, time=True
                ),
                # These are not rendered in the HTML (starting with underscore).
                "_score": pair.score,
                "_created_at": pair.created_at,
            }
            related_articles.append((article, meta))
            seen_articles[usafe] = pair.created_at

    related_articles.sort(
        key=lambda item: (item[1]["_score"], item[1]["_created_at"]), reverse=True
    )
    return render_template(
        "article.html",
        main_article=main_article,
        related_articles=related_articles,
    )
