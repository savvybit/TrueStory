"""Sends e-mails via SendGrid."""


import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from truestory import settings
from truestory import auth


def send_mail(to_mails, subject, text_content, html_content=None,
              from_mail=settings.DEFAULT_MAIL):
    html_content = html_content or text_content
    message = Mail(
        from_email=from_mail,
        to_emails=to_mails,
        subject=subject,
        plain_text_content=text_content,
        html_content=html_content,
    )
    client = SendGridAPIClient(auth.get_secret("sendgrid_key"))
    response = client.send(message)
    code = response.status_code
    logging.info("Email %s -> %s: %s (%d)", from_mail, to_mails, subject, code)
    if code // 100 != 2:
        raise Exception("Couldn't send e-mail: {} {}".format(code, response.body))
