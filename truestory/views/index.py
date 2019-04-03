"""Handles the '/' landing page."""


import logging

from flask import abort, jsonify, render_template, request

from truestory import app, auth
from truestory.models.mail import SubscriberModel


def _save_mail(mail):
    query = SubscriberModel.query()
    query.add_filter("mail", "=", mail)
    subscribers = SubscriberModel.all(query=query)

    if subscribers:
        assert len(subscribers) == 1
        subscriber = subscribers[0]
        if subscriber.subscribed:
            logging.warning("%r already subscribed.", mail)
            return False

        subscriber.subscribed = True
        subscriber.put()
        logging.info("%r re-subscribed.", mail)
        subscriber.send_greetings()
        return True

    subscriber = SubscriberModel(mail=mail)
    mail_key = subscriber.put()
    logging.info("New subscriber %r saved with key %r.", mail, mail_key)
    subscriber.send_greetings()
    return True


@app.route("/", methods=["GET", "POST"])
def index_view():
    """Main page standing for the presentation of the product."""
    if request.method == "POST":
        mail = request.form.get("mail", "").strip().lower()
        captcha_response = request.form.get("captchaResponse")
        if not all([mail, captcha_response]):
            return abort(400, "Captcha or e-mail not supplied.")

        try:
            valid = auth.validate_captcha(captcha_response)
        except Exception as exc:
            logging.exception("Captcha validation failed with %r.", exc)
            return abort(404, "Invalid captcha request/response.")
        if not valid:
            logging.warning("Wrong captcha response.")
            return abort(403, "Bad captcha response.")

        status = _save_mail(mail)
        return jsonify({"status": status})

    return render_template("index.html")
