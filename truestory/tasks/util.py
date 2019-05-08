"""Task creation helpers."""


import functools
import json
import logging

from flask import request, url_for
from flask_json import as_json
from google.cloud import tasks_v2

from truestory import app, settings
from truestory.views import base as views_base


TASK_HEADER = "X-AppEngine-TaskName"

app_client = app.test_client()
tasks_client = tasks_v2.CloudTasksClient()
require_headers = views_base.require_headers(
    TASK_HEADER, error_message="External requests are not allowed."
)


class create_task:

    """Convert any simple function into a task through this decorator."""

    ENCODING = settings.ENCODING

    def __init__(self, queue):
        self._queue = queue

    @property
    def route(self):
        return f"/task/{self._queue}"

    @classmethod
    def _serialize_args(cls, args, kwargs):
        return json.dumps({"args": args, "kwargs": kwargs}).encode(cls.ENCODING)

    @classmethod
    def _deserialize_args(cls, serialized):
        args_dict = json.loads(serialized)
        return args_dict["args"], args_dict["kwargs"]

    def _create_handler(self, function):
        @app.route(self.route, methods=["POST"])
        @require_headers
        @as_json
        @functools.wraps(function)
        def task_handler():
            """Generic task handler called by a successfully submitted task."""
            payload = request.get_data(as_text=True)
            if payload:
                args, kwargs = self._deserialize_args(payload)
                result = function(*args, **kwargs)
            else:
                result = function()
            return {"result": result}

    @classmethod
    def _debug_task(cls, function, args, kwargs):
        endpoint = function.__name__
        url = url_for(endpoint)
        data = cls._serialize_args(args, kwargs)
        headers = {TASK_HEADER: "test_task"}
        response = app_client.post(url, headers=headers, data=data)
        logging.debug("%s: %s", endpoint, response.json)

    def _create_task(self, args, kwargs):
        parent = tasks_client.queue_path(
            settings.PROJECT_ID, settings.LOCATION, self._queue
        )
        task = {
            "app_engine_http_request": {
                "http_method": "POST",
                "relative_uri": self.route,
                "body": self._serialize_args(args, kwargs),
            }
        }
        response = tasks_client.create_task(parent, task)
        logging.debug("Created task %s.", response.name)

    def __call__(self, function):
        self._create_handler(function)

        def wrapper(*args, **kwargs):
            if settings.DEBUG:
                self._debug_task(function, args, kwargs)
            else:
                self._create_task(args, kwargs)

        return wrapper
