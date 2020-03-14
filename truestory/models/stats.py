"""Various statistics."""


from truestory.models.base import BaseModel, SingletonMixin, ndb


class StatsModel(SingletonMixin, BaseModel):

    """Singleton stats model."""

    # up - True, down - False; per IP address.
    premium = ndb.JsonProperty(default={})
    topics = ndb.JsonProperty(default={})
