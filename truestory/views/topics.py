"""Handles the '/topics' page."""


from flask import render_template

from truestory import app


@app.route("/topics")
def topics_view():
    """Topics page displaying selectable favorite news subjects."""
    return render_template("topics.html")
