"""Base models and utilities used by the derived ones."""


import datetime
import logging

import ndb_orm as ndb
from google.cloud import datastore

from truestory import settings


NAMESPACE = "development" if settings.DEBUG else "production"

client = datastore.Client(project=settings.PROJECT_ID, namespace=NAMESPACE)
ndb.enable_use_with_gcd(client.project)


class BaseModel(ndb.Model):

    """Common model properties and functionality."""

    # String used for properties with no available data.
    NOT_SET = "N/A"

    created_at = ndb.DateTimeProperty(auto_now_add=True)

    def __init__(self, *args, project=settings.PROJECT_ID, namespace=NAMESPACE,
                 **kwargs):
        super().__init__(*args, project=project, namespace=namespace, **kwargs)

    @classmethod
    def model_name(cls):
        return cls.__name__.replace("Model", "")

    @classmethod
    def norm(cls, value):
        if value is None:
            return cls.NOT_SET
        return value

    @classmethod
    def query(cls, **kwargs):
        query = client.query(kind=cls._get_kind(), **kwargs)
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
        return client.get(self.key)

    @property
    def exists(self):
        """Checks if the entity is saved into the Datastore."""
        try:
            return bool(self.myself) if self.key and self.key.id else False
        except Exception:
            return False

    def put(self):
        """Saving the entity into the Datastore."""
        client.put(self)
        return self.key

    @staticmethod
    def put_multi(entities):
        client.put_multi(entities=entities)

    def remove(self):
        """Removes current entity and its dependencies (if any)."""
        client.delete(self.key)

    @property
    def usafe(self):
        return self.key.to_legacy_urlsafe()

    @classmethod
    def get(cls, urlsafe):
        key = ndb.Key(cls, project=settings.PROJECT_ID, namespace=NAMESPACE)
        item = client.get(key.from_legacy_urlsafe(urlsafe))
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
        keys = self.all(query=query, keys_only=True)
        return keys

    def put(self):
        """Check if already existing and if yes, replace the old values."""
        # Uniqueness by an ID property constraint for every extracted entity,
        # excluding the history ones if any (clones which are having the original
        # entity as `parent`).
        keys = self.get_existing()

        if self.exists or not keys:
            # Save the newly extracted entity or the already present one.
            return super().put()

        # Just update the already existing entity, without saving a new duplicate one.
        entity_id = getattr(self, self.primary_key())
        logging.debug("Updating already existing entity: %s.", entity_id)
        entity = keys[0].get(use_cache=False)
        return self._update(entity)
