"""Base models and utilities used by the derived ones."""


import datetime
import logging
import urllib.parse as urlparse
from collections import OrderedDict

from google.cloud import ndb

from truestory import settings


# Datastore default client settings.
PROJECT = settings.PROJECT_ID
# Number of entities to be put/removed at once.
MAX_BATCH_SIZE = 500

# Module level singleton client used in all DB interactions. This is lazy inited when
# is used only, so we don't have any issues with the Datastore agnostic tests or
# debugging, because creating a client will require valid credentials.
client = None
# Lazily loaded due to circular import (under SideMixin).
PreferencesModel = None


def ndb_kwargs(app=None):
    if not app:
        from truestory import app

    NAMESPACE = app.config["DATASTORE_NAMESPACE"]
    return {"project": PROJECT, "namespace": NAMESPACE}


def key_to_urlsafe(key):
    """Returns entity `key` as a string."""
    return key.urlsafe().decode(settings.ENCODING)


def urlsafe_to_key(urlsafe):
    """Returns entity from `urlsafe` string key."""
    key = ndb.Key(urlsafe=urlsafe, namespace=ndb_kwargs()["namespace"])
    return key


def batch_process(function, iterable, size=MAX_BATCH_SIZE):
    batch_returns = []
    iterable = list(iterable)
    for idx in range(0, len(iterable), size):
        subiter = iterable[idx:idx + size]
        batch_returns.append(function(subiter))
    return batch_returns


def get_client(app=None):
    """Singleton for the Datastore client."""
    global client
    if not client:
        client = ndb.Client(**ndb_kwargs(app=app))

    return client


class BaseModel(ndb.Model):

    """Common model properties and functionality."""

    # String used for properties with no available data (None).
    NOT_SET = "N/A"

    created_at = ndb.DateTimeProperty(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        kwargs.update(ndb_kwargs())
        super().__init__(*args, **kwargs)

    @classmethod
    def get_model_name(cls):
        """Returns the model name (without suffix)."""
        return cls.__name__.replace("Model", "")

    @classmethod
    def normalize(cls, value):
        """Normalizes a property value which needs to be rendered."""
        if value is None:
            return cls.NOT_SET
        return value

    @classmethod
    def all(cls, query=None, order=True, **kwargs):
        """Returns all the items in the DB created by this model.

        Args:
            query: Optionally you can supply a custom `query`.
            order (bool): Implicit by the time it was created in descending order.
        Returns:
            list: Fetched items.
        """
        query = query or cls.query()
        if order:
            query = query.order(-cls.created_at)
        return list(query.fetch(**kwargs))

    @property
    def myself(self):
        """Returns the current DB version of the same object."""
        return self.key.get(use_cache=False)

    @property
    def exists(self):
        """Checks if the entity is saved into the Datastore."""
        try:
            return bool(self.myself) if self.key and self.key.id else False
        except Exception:
            return False

    @classmethod
    def put_multi(cls, entities):
        """Multiple save in the DB without interfering with the `cls.put` function."""
        return batch_process(ndb.put_multi, entities)

    def remove(self):
        """Removes current entity and its dependencies (if covered and any)."""
        self.key.delete()

    @classmethod
    def remove_multi(cls, keys):
        """Multiple removal of entities based on the given `keys`."""
        batch_process(ndb.delete_multi, keys)

    @property
    def urlsafe(self):
        """Returns an URL safe Key string which uniquely identifies this entity."""
        return key_to_urlsafe(self.key)

    @classmethod
    def get(cls, urlsafe_or_key):
        """Retrieves an entity object based on an URL safe Key string or Key object."""
        if isinstance(urlsafe_or_key, (str, bytes)):
            complete_key = urlsafe_to_key(urlsafe_or_key)
        else:
            complete_key = urlsafe_or_key

        item = complete_key.get()
        if not item:
            raise Exception("item doesn't exist")
        return item


class DuplicateMixin:

    """Adds support for updating same entities when similar ones are added."""

    @property
    def primary_key(self):
        """Returns the property name holding an unique value among the others."""
        raise NotImplementedError(
            f"{self.get_model_name()} primary key not specified"
        )

    @property
    def primary_value(self):
        return getattr(self, self.primary_key)

    def get_existing(self):
        """Returns already existing entities based on the chosen `self.primary_key`.

        An existing entity is one that has the same primary key attribute value as the
        candidate's one.
        """
        primary_field = getattr(type(self), self.primary_key)
        query = self.query(primary_field == self.primary_value)
        keys = self.all(query=query, keys_only=True, order=False)
        return keys

    def update(self, duplicates):
        """Updates itself without creating another entry in the database."""
        logging.debug("Updating already existing entity: %s.", self.primary_value)
        assert len(duplicates) == 1, "found duplicate entity in the DB"
        entity = duplicates[0].get()
        properties = self.to_dict()
        properties["created_at"] = datetime.datetime.utcnow()
        entity.populate(**properties)
        return entity

    def put(self):
        """Check if this is already existing and if yes, just update with the new
        values.
        """
        # These are keys only entities.
        duplicates = self.get_existing()

        if self.exists or not duplicates:
            # Save the newly created entity or the already present one (self update).
            return super().put()

        return self.update(duplicates).put()

    @classmethod
    def put_multi(cls, entities):
        unique_entities = OrderedDict()
        for entity in entities:
            unique_entities[entity.primary_value] = entity

        for primary_value, entity in unique_entities.items():
            if entity.exists:
                continue

            duplicates = entity.get_existing()
            if duplicates:
                unique_entities[primary_value] = entity.update(duplicates)

        return super().put_multi(unique_entities.values())


class SideMixin:

    """Adds side info to a model."""

    LEFT = -2
    LEAN_LEFT = -1
    CENTER = 0
    LEAN_RIGHT = 1
    RIGHT = 2
    SIDE_MAPPING = {
        "Left": LEFT,
        "Lean Left": LEAN_LEFT,
        "Center": CENTER,
        "Lean Right": LEAN_RIGHT,
        "Right": RIGHT
    }
    SITE_REPLACE = ["www", "rss", "feeds"]
    _prefs = None

    side = ndb.IntegerProperty(required=True, choices=list(SIDE_MAPPING.values()))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.side is None:
            self.side = self._get_side(self.link, site=getattr(self, "site", None))

    @classmethod
    def normalize_site(cls, site):
        for repl in cls.SITE_REPLACE:
            site = site.replace(repl, "", 1)
        return site.strip(".-")

    @classmethod
    def url_to_site(cls, url):
        return cls.normalize_site(urlparse.urlsplit(url).netloc)

    @classmethod
    def _get_prefs(cls):
        if not cls._prefs:
            global PreferencesModel
            if not PreferencesModel:
                from truestory.models.preferences import PreferencesModel
            cls._prefs = PreferencesModel.instance()
        return cls._prefs

    @classmethod
    def get_site_info(cls, link, site=None):
        site = site or cls.url_to_site(link)
        site_info = cls._get_prefs().sites.get(site)
        if not site_info:
            raise Exception(f"item coming from unrecognized source {site!r}")

        return site, site_info

    @classmethod
    def _get_side(cls, link, site):
        if not link:
            return None

        _, site_info = cls.get_site_info(link, site=site)
        return cls.SIDE_MAPPING[site_info["side"]]


class SingletonMixin:

    """Singleton support for models."""

    @classmethod
    def instance(cls):
        entities = cls.all()
        if not entities:
            logging.info("Creating %s model for the first time.", cls)
            instance = cls()
            instance.put()
            entities = cls.all()
        assert len(entities) == 1, f"duplicate {cls} objects"
        return entities[0]
