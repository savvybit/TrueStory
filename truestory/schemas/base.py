"""Augment and customize schemas behavior."""


import flask
from flask_marshmallow.schema import sentinel

from truestory import ma


class Schema(ma.Schema):

    def jsonify(self, obj, many=sentinel, _name=None, *args, **kwargs):
        """Extends current JSON with `kwargs` and returns a dict-like response each
        time.
        """
        resp = super().jsonify(obj, many=many, *args)
        # Since `kwargs` doesn't go along any arg(s), we'll be merging it with the
        # original response JSON.
        data = {_name: resp.json, **kwargs}
        return flask.jsonify(data)
