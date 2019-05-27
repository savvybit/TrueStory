"""Handles the '/cron/*' jobs."""


from flask_json import as_json

from truestory import app
from truestory.tasks import clean_articles, crawl_articles
from truestory.views import base


require_headers = base.require_headers(
    "X-Appengine-Cron", error_message="External requests are not allowed."
)


@app.route("/cron/crawl")
@require_headers
@as_json
def cron_crawl_view():
    """Spawns a new crawler for each individual target."""
    return {"crawled": crawl_articles()}


@app.route("/cron/clean")
@require_headers
@as_json
def cron_clean_view():
    """Clean-ups every outdated article or bias pair."""
    return {"cleaned": clean_articles()}
