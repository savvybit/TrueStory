"""Handles individual '/article' page."""


from flask import render_template

from truestory import app
from truestory.models.article import ArticleModel, BiasPairModel


@app.route("/article/<article_usafe>")
def article(article_usafe):
    """Displays article details and its opposed ones."""
    main_article = ArticleModel.get(article_usafe)
    related_articles = []

    complementary = {"left": "right", "right": "left"}
    for side in complementary:
        query = BiasPairModel.query()
        query.add_filter(side, "=", main_article.key)
        pairs = list(query.fetch())
        related_articles.extend([
            getattr(pair, complementary[side]).get() for pair in pairs
        ])

    return render_template(
        "article.html",
        main_article=main_article,
        related_articles=related_articles,
    )
