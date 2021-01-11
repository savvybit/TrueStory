"""Handles the '/home' page."""


from flask import jsonify, render_template, request, url_for
from google.cloud.ndb._datastore_query import Cursor

from truestory import app, settings
from truestory.models.article import BiasPairModel
from truestory.views import base as views_base


def _get_serializable_article(article_key):
    """JSON serializable article format used by the front-end ajax calls."""
    article = article_key.get()
    # NOTE(cmiN): Sometimes even if the article was long removed, the pagination
    #  iterates through existing keys pointing to missing articles.
    if not article:
        return None

    paragraph_split = lambda text: (
        "\n".join(views_base.paragraph_split_filter(text)) if text else ""
    )
    details = article.to_dict()
    details.update({
        "usafe": url_for("article_view", article_usafe=article.urlsafe),
        "link": views_base.website_filter(details["link"]),
        "content": paragraph_split(details["content"]),
        "summary": paragraph_split(details["summary"]),
        "authors": views_base.join_authors_filter(details["authors"]),
        "published": views_base.format_date_filter(details["published"], time=True),
    })
    return details


@app.route("/home")
@views_base.require_auth
def home_view():
    """Home page displaying news and available app components."""
    search = request.args.get("querySearch", "").strip().lower()
    cursor_usafe = request.args.get("queryCursor")

    query = BiasPairModel.query()
    if search:
        tokens = search.split()
        # All the provided tokens should be among the keywords.
        for token in tokens:
            query = query.filter(BiasPairModel.keywords.IN([token]))

    query = query.order(-BiasPairModel.score, -BiasPairModel.created_at)
    start_cursor = Cursor(urlsafe=cursor_usafe)
    bias_pairs, next_cursor, more = query.fetch_page(3, start_cursor=start_cursor)
    if more:
        next_cursor_usafe = (next_cursor.urlsafe() if next_cursor else b"").decode(
            settings.ENCODING
        )
    else:
        next_cursor_usafe = ""

    if cursor_usafe:
        pairs = []
        for pair in bias_pairs:
            left_dict, right_dict = map(
                _get_serializable_article, (pair.left, pair.right)
            )
            pair = (left_dict, right_dict)
            if all(pair):
                pairs.append(pair)
        return jsonify({"bias_pairs": pairs, "new_cursor": next_cursor_usafe})

    return render_template(
        "home.html",
        title="Search results" if search else None,
        bias_pairs=bias_pairs,
        query_search=search,
        query_cursor=next_cursor_usafe,
    )
