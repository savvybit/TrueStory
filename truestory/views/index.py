"""Handles the '/' landing page."""


from flask import render_template

from truestory import app


@app.route("/")
def index_view():
    """Main page standing for the presentation of the product."""
    extension_url = (
        "https://chrome.google.com/webstore/detail/truestory/"
        "elknkoobodlilnddeeiehnaepdahhnpm"
    )
    return render_template("index.html", extension_url=extension_url)
