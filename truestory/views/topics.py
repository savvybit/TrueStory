"""Handles the '/topics' page."""


from flask import render_template

from truestory import app
from truestory.views import base as views_base


@app.route("/topics")
@views_base.require_auth
def topics_view():
    """Topics page displaying selectable favorite news subjects."""
    return render_template("topics.html")
