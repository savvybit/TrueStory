"""Global admin settings, options and preferences."""


from truestory.models.base import BaseModel, SingletonMixin, ndb


class PreferencesModel(SingletonMixin, BaseModel):

    """Singleton preferences and resources model."""

    sites = ndb.JsonProperty(default={})
    contradiction_threshold = ndb.FloatProperty(default=0.5)
    similarity_threshold = ndb.FloatProperty(default=0.5)
