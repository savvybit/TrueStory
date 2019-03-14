"""All views and routes exposed by the web app."""


from . import article, base, home, index, topics
from .. import app


@app.route("/favicon.ico")
def favicon():
    """Serves the web icon from the static images."""
    return app.send_static_file("img/favicon.ico")


@app.route("/debug")
def debug():
    """Triggers debugger on local environment only."""
    assert app.debug is False
