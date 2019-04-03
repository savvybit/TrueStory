"""E-mails storage."""


import datetime
import hashlib

from truestory import app, mail as mail_util, settings
from truestory.models.base import BaseModel, ndb


def render_template(path, **kwargs):
    template = app.jinja_env.get_template(path)
    return template.render(**kwargs)


class SubscriberModel(BaseModel):

    """Subscriber e-mail got from the landing page."""

    mail = ndb.StringProperty(required=True)
    hashsum = ndb.StringProperty(required=True)
    subscribed = ndb.BooleanProperty(default=True)

    def put(self):
        date = datetime.datetime.utcnow()
        string = f"{self.mail}_{date.isoformat()}"
        self.hashsum = hashlib.md5(string.encode(settings.ENCODING)).hexdigest()
        return super().put()

    def send_greetings(self):
        """Sends greetings e-mail to our new subscriber."""
        text_content = render_template("mail/greetings.txt")
        html_content = render_template("mail/greetings.html")
        mail_util.send_mail(
            self.mail, "Subscribed to TrueStory",
            text_content=text_content, html_content=html_content
        )
