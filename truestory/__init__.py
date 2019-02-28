from flask import Flask

from . import config, settings
from .settings import LOGFILE


app = Flask(__name__)
app.config.from_object(config.config[settings.CONFIG])


from . import views
