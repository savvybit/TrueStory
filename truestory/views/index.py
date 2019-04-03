"""Handles the '/' landing page."""


import logging

from flask import abort, jsonify, render_template, request

from truestory import app, auth
from truestory.models.mail import SubscriberModel


def _subscribe_mail(mail):
    """Adds a new subscriber to our platform.

    Returns:
        SubscriberModel: The newly added subscriber, currently updated one or None if
        the provided `mail` is already subscribed.
    """
    query = SubscriberModel.query()
    query.add_filter("mail", "=", mail)
    subscribers = SubscriberModel.all(query=query)

    if subscribers:
        assert len(subscribers) == 1
        subscriber = subscribers[0]
        if subscriber.subscribed:
            logging.warning("%r already subscribed.", mail)
            return None

        subscriber.subscribed = True
        subscriber.put()
        logging.info("%r re-subscribed.", mail)
        return subscriber

    subscriber = SubscriberModel(mail=mail)
    mail_key = subscriber.put()
    logging.info("New subscriber %r saved with key %r.", mail, mail_key)
    return subscriber


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

        subscriber = _subscribe_mail(mail)
        if subscriber:
            subscriber.send_greetings()
        return jsonify({"status": bool(subscriber)})

    return render_template("index.html")
