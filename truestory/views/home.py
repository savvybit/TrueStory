"""Handles the home page."""


from flask import render_template

from truestory import app


@app.route("/home")
def home():
    """Home page displaying news and available app components."""
    return render_template("home.html")
