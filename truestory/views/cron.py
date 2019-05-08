"""Handles the '/cron/*' jobs."""


from flask_json import as_json

from truestory import app
from truestory.tasks import crawl_articles
from truestory.views import base


require_headers = base.require_headers(
    "X-Appengine-Cron", error_message="External requests are not allowed."
)


@app.route("/cron/crawl")
@require_headers
@as_json
def cron_crawl_view():
    """Spawns a new crawler for each individual target."""
    count = crawl_articles()
    return {"targets": count}


@app.route("/cron/bias")
@require_headers
@as_json
def cron_bias_view():
    """Creates relevant bias pairs out of recent articles."""
    return {"test": 1}


@app.route("/cron/clean")
@require_headers
@as_json
def cron_clean_view():
    """Clean-ups every outdated article or bias pair."""
    return {"test": 1}
