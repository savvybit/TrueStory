"""Handles the '/premium' page."""


from flask import render_template, request

from truestory import app, get_remote_address
from truestory.models import StatsModel
from truestory.views import base as views_base


def _save_thumbs(up):
    stats = StatsModel.instance()
    address = get_remote_address()
    stats.thumbs[address] = up
    stats.put()


def _get_thumbs():
    stats = StatsModel.instance()
    address = get_remote_address()
    return stats.thumbs.get(address)


@app.route("/premium")
@views_base.require_auth
def premium_view():
    """Premium page displaying the ability to buy pro access."""
    thumbs = request.args.get("thumbs", "").lower()
    if thumbs == "up":
        _save_thumbs(True)
    elif thumbs == "down":
        _save_thumbs(False)
    if not thumbs:
        thumbs = _get_thumbs()
        if thumbs is not None:
            thumbs = "up" if thumbs else "down"
    return render_template("premium.html", thumbs=thumbs)
