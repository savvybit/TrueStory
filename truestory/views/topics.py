"""Handles the '/topics' page."""


from flask import render_template, request

from truestory import app
from truestory.views import base as views_base


@app.route("/topics")
@views_base.require_auth
def topics_view():
    """Topics page displaying selectable favorite news subjects."""
    topics = app.config["CONFIG"].topics

    thumbs = request.args.get("thumbs", "").lower()
    if thumbs:
        thumbs = thumbs == "up"
        topic = request.args.get("topic")
        views_base.save_thumbs("topics", topic, thumbs=thumbs)

    thumbs = views_base.get_thumbs("topics")
    return render_template(
        "topics.html", topics=topics, thumbs=thumbs, typeform_text="think"
    )
