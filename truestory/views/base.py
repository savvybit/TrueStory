"""Base views, routes and utilities used by the web app's views."""


from truestory import app
from truestory.models import base as models_base


@app.template_filter("norm")
def norm_filter(value):
    """Normalizes the None value (check if property is empty/missing)."""
    return models_base.BaseModel.normalize(value)


@app.template_filter("usafe")
def usafe_filter(entity):
    """Returns the URL safe key string given an entity."""
    return entity.urlsafe


@app.template_filter("format_date")
def format_date_filter(date, time=False):
    """Returns a formatted date string out of a `datetime` object.

    Args:
        time (bool): Add to date the time too if this is True.
    """
    if not date:
        return date
    template = "%d-%m-%y"
    if time:
        template += " %H:%M"
    return date.strftime(template)
