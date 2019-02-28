"""Handles the front page."""


from flask import render_template

from truestory import app


@app.route("/")
def index():
    """Main page standing for presentation of the product."""
    return render_template("index.html")
