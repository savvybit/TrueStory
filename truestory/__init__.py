"""Entry point for the entire library (app initialization)."""


import logging

from flask import Blueprint, Flask
from flask_cors import CORS
from flask_json import FlaskJSON
from flask_marshmallow import Marshmallow
from flask_restful import Api

from . import config, settings
from .settings import LOGFILE


level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
    level=level
)
config.init_datastore_emulator()

app = Flask(__name__)
CORS(app)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.config.from_object(config.config[settings.CONFIG])

json = FlaskJSON(app)

api_bp = Blueprint("api", __name__)
api = Api(api_bp)
app.register_blueprint(api_bp, url_prefix="/api")

ma = Marshmallow(app)


# Due to circular imports and for routing to take effect.
from . import resources, views


api.errors = resources.ERRORS
