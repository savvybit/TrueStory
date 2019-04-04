"""Entry point for the entire library (app initialization)."""


import logging

from flask import Flask

from . import config, settings
from .settings import LOGFILE


level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
    level=level
)

app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.config.from_object(config.config[settings.CONFIG])


from . import views
