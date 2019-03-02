"""All views and routes exposed by the web app."""


from . import index
from .. import app


@app.route("/debug")
def debug():
    """Trigger debugger on local environment only."""
    assert app.debug is False
