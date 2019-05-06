"""Handles the '/login' page."""


from flask import redirect, render_template, request, session, url_for

from truestory import app


@app.route("/login", methods=["GET", "POST"])
def login_view():
    """Asks user for a token key."""
    if request.method == "POST":
        session["token"] = request.form.get("token")
        return redirect(url_for("home_view"))

    return render_template("login.html")
