"""Handles the '/login' page."""


from flask import abort, redirect, render_template, request, session, url_for

from truestory import app, auth


@app.route("/login", methods=["GET", "POST"])
def login_view():
    """Asks user for a token key."""
    next_url = request.args.get("next", "").strip()

    if request.method == "POST":
        session["token"] = request.form.get("token")
        url = next_url or url_for("home_view")
        return redirect(url)

    return render_template("login.html", next=next_url)


@app.route("/token")
def token_view():
    """Returns the shared token to the public."""
    limiter_conf = app.config["CONFIG"].rate_limiter
    for email in limiter_conf.emails:
        if email.share:
            token = auth.compute_token(email.email)
            if auth.authorize_with_token(token):
                return token
    abort(403)
