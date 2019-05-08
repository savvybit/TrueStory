"""Task creation helpers."""


import functools
import json
import logging

from flask import request, url_for
from flask_json import as_json
from google.cloud import tasks_v2

from truestory import app, settings


app_client = app.test_client()
tasks_client = tasks_v2.CloudTasksClient()


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

    def _create_handler(self, func):
        @app.route(self.route, methods=["POST"])
        @as_json
        @functools.wraps(func)
        def task_handler():
            """Generic task handler called by a successfully submitted task."""
            payload = request.get_data(as_text=True)
            if payload:
                args, kwargs = self._deserialize_args(payload)
                result = func(*args, **kwargs)
            else:
                result = func()
            return {"result": result}

    @classmethod
    def _debug_task(cls, func, args, kwargs):
        endpoint = func.__name__
        url = url_for(endpoint)
        data = cls._serialize_args(args, kwargs)
        response = app_client.post(url, data=data)
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

    def __call__(self, func):
        self._create_handler(func)

        def wrapper(*args, **kwargs):
            if settings.DEBUG:
                self._debug_task(func, args, kwargs)
            else:
                self._create_task(args, kwargs)

        return wrapper
