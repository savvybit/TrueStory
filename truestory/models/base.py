"""Base models and utilities used by the derived ones."""


import datetime
import logging

import ndb_orm as ndb
from google.cloud import datastore

from truestory import app, settings


# Datastore default client settings.
PROJECT = settings.PROJECT_ID
NAMESPACE = app.config["DATASTORE_NAMESPACE"]
NDB_KWARGS = {"project": PROJECT, "namespace": NAMESPACE}

# Module level singleton client used in all DB interactions. This is lazy inited when
# is used only, so we don't have any issues with the Datastore agnostic tests or
# debugging, because creating a client will require valid credentials.
client = None


class BaseModel(ndb.Model):

    """Common model properties and functionality."""

    # String used for properties with no available data (None).
    NOT_SET = "N/A"

    created_at = ndb.DateTimeProperty(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        self._get_client()  # Activates all NDB ORM required features.
        kwargs.update(NDB_KWARGS)
        super().__init__(*args, **kwargs)

    @classmethod
    def model_name(cls):
        """Returns the model name (without suffix)."""
        return cls.__name__.replace("Model", "")

    @classmethod
    def normalize(cls, value):
        """Normalizes a property value which needs to be rendered."""
        if value is None:
            return cls.NOT_SET
        return value

    @staticmethod
    def _get_client():
        """Singleton for the Datastore client."""
        global client
        if not client:
            client = datastore.Client(**NDB_KWARGS)
            ndb.enable_use_with_gcd(client=client, **NDB_KWARGS)
        return client

    @classmethod
    def query(cls, **kwargs):
        """Creates a Datastore query out of this model."""
        query = cls._get_client().query(kind=cls._get_kind(), **kwargs)
        return query

    @classmethod
    def all(cls, query=None, keys_only=False, **kwargs):
        """Returns all the items in the DB created by this model.

        Args:
            query: Optionally you can supply a custom `query`.
            keys_only (bool): Keep the Key properties only if this is True.
        Returns:
            list: Fetched items.
        """
        query = query or cls.query()
        query.order = ["-created_at"]
        if keys_only:
            query.keys_only()
        return list(query.fetch(**kwargs))

    @property
    def myself(self):
        """Returns the current DB version of the same object."""
        return self.key.get()

    @property
    def exists(self):
        """Checks if the entity is saved into the Datastore."""
        try:
            return bool(self.myself) if self.key and self.key.id else False
        except Exception:
            return False

    def put(self):
        """Saves the entity into the Datastore."""
        self._get_client().put(self)
        return self.key

    @classmethod
    def put_multi(cls, entities):
        """Multiple save in the DB without interfering with the `cls.put` function."""
        cls._get_client().put_multi(entities)
        return [entity.key for entity in entities]

    def remove(self):
        """Removes current entity and its dependencies (if covered and any)."""
        self.key.delete()

    @classmethod
    def remove_multi(cls, keys):
        """Multiple removal of entities based on the given `keys`."""
        cls._get_client().delete_multi(keys)

    @property
    def urlsafe(self):
        """Returns an URL safe Key string which uniquely identifies this entity."""
        return self.key.to_legacy_urlsafe().decode(settings.ENCODING)

    @classmethod
    def get(cls, urlsafe_or_key):
        """Retrieves an entity object based on an URL safe Key string or Key object."""
        if isinstance(urlsafe_or_key, (str, bytes)):
            key = ndb.Key(cls, **NDB_KWARGS)
            complete_key = key.from_legacy_urlsafe(urlsafe_or_key)
        else:
            complete_key = urlsafe_or_key

        item = complete_key.get()
        if not item:
            raise Exception("item doesn't exist")
        return item


class DuplicateMixin:

    """Adds support for updating same entities when similar ones are added."""

    @classmethod
    def primary_key(cls):
        """Returns the property name holding an unique value among the others."""
        raise NotImplementedError(
            f"{cls.model_name()} primary key not specified"
        )

    def _update(self, entity):
        """Updates itself without creating another entry in the database."""
        properties = self.to_dict()
        properties["created_at"] = datetime.datetime.utcnow()
        entity.populate(**properties)
        return entity.put()

    def get_existing(self):
        """Returns already existing entities based on the chosen `self.primary_key`.

        An existing entity is one that has the same primary key attribute value as the
        candidate's one.
        """
        cls = type(self)
        prop = cls.primary_key()
        src = getattr(self, prop)
        query = cls.query()
        query.add_filter(prop, "=", src)
        entities = self.all(query=query, keys_only=True)
        return entities

    def put(self):
        """Check if this is already existing and if yes, just update with the new
        values.
        """
        # These are keys only entities.
        entities = self.get_existing()

        if self.exists or not entities:
            # Save the newly created entity or the already present one (self update).
            return super().put()

        # Just update the already existing entity, without saving a new duplicate.
        entity_id = getattr(self, self.primary_key())
        logging.debug("Updating already existing entity: %s.", entity_id)
        # Should have one exemplary only.
        assert len(entities) == 1, "found duplicate entity in the DB"
        entity = entities[0].myself
        return self._update(entity)
