"""Entry point for the entire library (app initialization)."""


import logging

from flask import Blueprint, Flask
from flask_marshmallow import Marshmallow
from flask_restful import Api

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

api_bp = Blueprint("api", __name__)
api = Api(api_bp)
app.register_blueprint(api_bp, url_prefix="/api")

ma = Marshmallow(app)


from . import resources, views
