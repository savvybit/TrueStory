"""Handles the '/login' page."""


from flask import redirect, render_template, request, session, url_for

from truestory import app


@app.route("/login")
def login_view():
    """Asks user for a token key."""
    token = request.args.get("token")
    if token:
        session["token"] = token
        return redirect(url_for("home_view"))

    return render_template("login.html")
