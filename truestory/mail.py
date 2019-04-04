"""Sends e-mails via SendGrid."""


import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from truestory import auth, settings


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

    if settings.DEBUG:
        code = 200
    else:
        client = SendGridAPIClient(auth.get_secret("sendgrid_key"))
        response = client.send(message)
        code = response.status_code
        was_successful = lambda ret_code: ret_code // 100 in (2, 3)
        if not was_successful(code):
            raise Exception("Couldn't send e-mail: {} {}".format(code, response.body))

    logging.info(
        "E-mail sent %s -> %s: %r (%d - %s)", from_mail, to_mails, subject, code,
        "dry run" if settings.DEBUG else "for real"
    )
