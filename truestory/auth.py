"""Tackles authentication and authorization."""


import hmac
import pkg_resources

from truestory import app, settings


def compute_token(mail):
    return hmac.new(app.secret_key, mail.encode(settings.ENCODING)).hexdigest()


def authorize_with_token(token):
    content = pkg_resources.resource_string("truestory", "secrets/auth_mails")
    mails = content.decode(settings.ENCODING).strip().splitlines()
    tokens = map(compute_token, mails)
    return token in tokens
