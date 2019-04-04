"""Handles user (un)subscription."""


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
        assert len(subscribers) == 1, "duplicate subscriber mail"
        subscriber = subscribers[0]
        if subscriber.subscribed:
            logging.warning("%r already subscribed.", mail)
            return None

        subscriber.subscribed = True
        subscriber.put()
        logging.info("%r re-subscribed.", mail)
        return subscriber

    subscriber = SubscriberModel(mail=mail)
    subscriber_key = subscriber.put()
    logging.info("New subscriber %r saved with key %r.", mail, subscriber_key)
    return subscriber


@app.route("/subscribe", methods=["POST"])
def subscribe_view():
    """Subscribes a new visitor through the landing page."""
    mail = request.form.get("mail", "").strip().lower()
    captcha_response = request.form.get("captchaResponse")
    if not all([mail, captcha_response]):
        logging.warning("Didn't receive the e-mail or captcha.")
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
        subscriber.send_greetings(request.url_root)
    return jsonify({"status": bool(subscriber)})


@app.route("/unsubscribe/<hashsum>")
def unsubscribe_view(hashsum):
    """Un-subscribes a fan through the URL provided by mail."""
    query = SubscriberModel.query()
    query.add_filter("hashsum", "=", hashsum)
    subscribers = list(query.fetch())
    assert len(subscribers) in (0, 1), "duplicate subscriber mail"

    if subscribers:
        subscriber = subscribers[0]
        status = subscriber.subscribed
        if status:
            subscriber.subscribed = False
            subscriber.put()
            message = "Unsubscribed successfully."
        else:
            message = "You're already unsubscribed."
    else:
        status = False
        message = "Couldn't find you!"

    return render_template("unsubscribe.html", status=status, message=message)
