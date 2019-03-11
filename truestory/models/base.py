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
# is used only, so we don't have any issues with Datastore agnostic tests/debugging,
# because creating a client will require valid credentials.
client = None

# Save original `KeyProperty` class because we'll be overriding it.
KeyProperty = ndb.KeyProperty


class NamespacedKeyProperty(KeyProperty):

    def _db_get_value(self, v):
        """Same as original function, but adds the `namespace` too."""
        key = super()._db_get_value(v)
        return ndb.key_module.Key(
            *key.flat_path, project=key.project,
            namespace=v.key_value.partition_id.namespace_id
        )


ndb.KeyProperty = NamespacedKeyProperty


class BaseModel(ndb.Model):

    """Common model properties and functionality."""

    # String used for properties with no available data.
    NOT_SET = "N/A"

    created_at = ndb.DateTimeProperty(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        self._get_client()  # Activates all NDB ORM required features.
        kwargs.update(NDB_KWARGS)
        super().__init__(*args, **kwargs)

    @classmethod
    def model_name(cls):
        return cls.__name__.replace("Model", "")

    @classmethod
    def normalize(cls, value):
        if value is None:
            return cls.NOT_SET
        return value

    @staticmethod
    def _get_client():
        global client
        if not client:
            client = datastore.Client(**NDB_KWARGS)
            ndb.enable_use_with_gcd(**NDB_KWARGS)
        return client

    @classmethod
    def query(cls, **kwargs):
        query = cls._get_client().query(kind=cls._get_kind(), **kwargs)
        return query

    @classmethod
    def all(cls, query=None, keys_only=False, **kwargs):
        query = query or cls.query()
        query.order = ["-created_at"]
        if keys_only:
            query.keys_only()
        return list(query.fetch(**kwargs))

    @property
    def myself(self):
        """Return the current DB version of the same object."""
        return self._get_client().get(self.key)

    @property
    def exists(self):
        """Checks if the entity is saved into the Datastore."""
        try:
            return bool(self.myself) if self.key and self.key.id else False
        except Exception:
            return False

    def put(self):
        """Saving the entity into the Datastore."""
        self._get_client().put(self)
        return self.key

    @classmethod
    def put_multi(cls, entities):
        """Multiple save in the DB without interfering with `cls.put` function."""
        cls._get_client().put_multi(entities)
        return [entity.key for entity in entities]

    def remove(self):
        """Removes current entity and its dependencies (if any)."""
        self._get_client().delete(self.key)

    @classmethod
    def remove_multi(cls, keys):
        cls._get_client().delete_multi(keys)

    @property
    def urlsafe(self):
        return self.key.to_legacy_urlsafe().decode(settings.ENCODING)

    @classmethod
    def get(cls, urlsafe_or_key):
        if isinstance(urlsafe_or_key, (str, bytes)):
            key = ndb.Key(cls, **NDB_KWARGS)
            urlsafe_or_key = key.from_legacy_urlsafe(urlsafe_or_key)
        item = cls._get_client().get(urlsafe_or_key)
        if not item:
            raise Exception("item doesn't exist")
        return item


class DuplicateMixin:

    """Adds support for updating same entities when similar ones are added."""

    @classmethod
    def primary_key(cls):
        """Returns the property name holding unique values."""
        raise NotImplementedError(
            f"{cls.model_name()} primary key not specified"
        )

    def _update(self, entity):
        """Update itself without creating history."""
        # Update the old entity with the newly extracted values (from self).
        properties = self.to_dict()  # without the skips ofc
        # Make sure we put the current date.
        properties["created_at"] = datetime.datetime.utcnow()
        # Populate the original existing entity with all the non skip-able properties.
        entity.populate(**properties)
        # Save all the new incoming changes into the old entity.
        return entity.put()

    def get_existing(self):
        """Returns already existing entity keys based on the given `parent`.

        An existing entity is one that has the same primary key attribute as the
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
        """Check if already existing and if yes, replace the old values."""
        # All similar entities (based on ID) containing keys only.
        entities = self.get_existing()

        if self.exists or not entities:
            # Save the newly extracted entity or the already present one.
            return super().put()

        # Just update the already existing entity, without saving a new duplicate one.
        entity_id = getattr(self, self.primary_key())
        logging.debug("Updating already existing entity: %s.", entity_id)
        # Get back the full entity.
        entity = entities[0].myself
        return self._update(entity)
