"""Handles the '/' landing page."""


import logging

from flask import abort, jsonify, render_template, request

from truestory import app, auth
from truestory.models.mail import MailModel


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

        query = MailModel.query()
        query.add_filter("mail", "=", mail)
        mails = MailModel.all(query=query, keys_only=True)
        if mails:
            logging.warning("%r already subscribed.", mail)
            return jsonify({"status": False})

        mail_key = MailModel(mail=mail).put()
        logging.info("New subscriber %r saved with key %r.", mail, mail_key)
        return jsonify({"status": True})

    return render_template("index.html")
