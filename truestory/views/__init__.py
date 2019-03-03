"""All views and routes exposed by the web app."""


from . import home, index
from .. import app


@app.route("/favicon.ico")
def favicon():
    """Serves web icon from the static images."""
    return app.send_static_file("img/favicon.ico")


@app.route("/debug")
def debug():
    """Trigger debugger on local environment only."""
    assert app.debug is False
