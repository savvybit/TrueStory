"""Tackles authentication and authorization."""


import hmac

from truestory import app, settings


AUTH_PATH = settings.PROJECT_DIR / "secrets" / "auth_mails"


def compute_token(mail):
    return hmac.new(app.secret_key, mail.encode(settings.ENCODING)).hexdigest()


def authorize_with_token(token):
    with open(AUTH_PATH, "r") as stream:
        mails = stream.read().strip().splitlines()
    tokens = map(compute_token, mails)
    return token in tokens
