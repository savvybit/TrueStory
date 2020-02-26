"""Various statistics."""


from truestory.models.base import BaseModel, SingletonMixin, ndb


class StatsModel(SingletonMixin, BaseModel):

    """Singleton stats model."""

    # up - True, down - False; per IP address.
    thumbs = ndb.JsonProperty(default={})
