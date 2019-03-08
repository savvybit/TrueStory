"""Handles individual article page."""


from flask import render_template

from truestory import app
from truestory.models.article import ArticleModel


@app.route("/article/<article_usafe>")
def article(article_usafe):
    """Displays article details and its opposed ones."""
    return render_template("article.html")
