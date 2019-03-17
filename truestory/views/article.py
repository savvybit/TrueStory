"""Handles individual '/article' page."""


from flask import render_template

from truestory import app
from truestory.models.article import ArticleModel, BiasPairModel


@app.route("/article/<article_usafe>")
def article_view(article_usafe):
    """Displays article details and its opposed ones."""
    main_article = ArticleModel.get(article_usafe)
    related_articles = []

    complementary = {"left": "right", "right": "left"}
    for side in complementary:
        query = BiasPairModel.query()
        query.add_filter(side, "=", main_article.key)
        pairs = list(query.fetch())

        for pair in pairs:
            article = getattr(pair, complementary[side]).get()
            related_articles.append((article, pair.score))

    return render_template(
        "article.html",
        main_article=main_article,
        related_articles=related_articles,
    )
