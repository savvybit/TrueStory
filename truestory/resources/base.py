"""Base API views and functions."""


import functools

from flask_restful import Resource, abort, request

from truestory import auth


def get_auth_token():
    auth_parts = request.headers.get("Authorization", "").strip().split()
    if len(auth_parts) != 2:
        return None

    kind, token = auth_parts
    if kind == "Bearer" and token:
        return token

    return None


def _authenticate(func):
    """Checks for authentication token within headers."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = get_auth_token()
        if token and auth.authorize_with_token(token):
            return func(*args, **kwargs)
        abort(401, message="Invalid or missing token.")

    return wrapper


class BaseResource(Resource):

    """Base resource API handler."""

    URL_PREFIX = ENDPOINT = ""
    SEP = "_"
    method_decorators = [_authenticate]

    @classmethod
    def get_route(cls):
        """Returns the string route for the current resource."""
        return f"{cls.URL_PREFIX}/{cls.ENDPOINT}"

    @classmethod
    def get_endpoint(cls):
        """Returns the endpoint name for the current resource."""
        return f"{cls.URL_PREFIX}{cls.SEP}{cls.ENDPOINT}".strip("/")


class DatastoreMixin:

    """Mixin handling database serialization of entities."""

    @staticmethod
    def _get_schemas():
        raise NotImplementedError("required schemas not provided")

    @classmethod
    def _make_response(cls, which, obj, **kwargs):
        schema = cls._get_schemas()[which]
        return schema.jsonify(obj, _name=which, **kwargs)
