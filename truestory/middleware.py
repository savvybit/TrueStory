"""Request interceptors for augmenting the flow."""


import functools

from google.cloud.ndb import context as context_module

from truestory.models import get_client


def ndb_wsgi_middleware(app):
    client = get_client(app=app)
    wsgi_app = app.wsgi_app

    @functools.wraps(wsgi_app)
    def middleware(*args, **kwargs):
        if context_module.get_context(False):
            return wsgi_app(*args, **kwargs)

        with client.context():
            return wsgi_app(*args, **kwargs)

    app.wsgi_app = middleware
