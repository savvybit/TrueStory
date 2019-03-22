from flask import Flask

from . import config, settings
from .settings import LOGFILE


app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.config.from_object(config.config[settings.CONFIG])


from . import views
