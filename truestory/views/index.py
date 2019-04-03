"""Handles the '/' landing page."""


from flask import render_template

from truestory import app


@app.route("/")
def index_view():
    """Main page standing for the presentation of the product."""
    return render_template("index.html")
