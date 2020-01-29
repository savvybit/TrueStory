"""Entry point for the entire library (app initialization)."""


import logging

from flask import Blueprint, Flask
from flask_cors import CORS
from flask_json import FlaskJSON
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr as get_remote_address
from flask_marshmallow import Marshmallow
from flask_restful import Api

from . import config, settings
from .settings import LOGFILE


level = logging.DEBUG if settings.GAE_DEBUG else logging.INFO
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

# NOTE(cmiN): Remember that the original `get_remote_address` always returns
#  "127.0.0.1" under GAE deployment.
limiter = Limiter(app, key_func=get_remote_address)

api_bp = Blueprint("api", __name__)
api = Api(api_bp)
app.register_blueprint(api_bp, url_prefix="/api")

ma = Marshmallow(app)


# Due to circular imports and for routing to take effect.
from . import resources, views


api.errors = resources.ERRORS
