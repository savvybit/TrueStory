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

    # String used for properties with not available data.
    NOT_SET = "N/A"

    created_at = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def all(cls, query=None, **kwargs):
        query = query or cls.query()
        return query.order(-cls.created_at).fetch(**kwargs)

    @classmethod
    def norm(cls, value):
        if value is None:
            return cls.NOT_SET
        return value

    @property
    def myself(self):
        """Return the current DB version of the same object (without caching)."""
        return self.key.get(use_cache=False, use_memcache=False)

    @property
    def exists(self):
        """Checks if the entity is saved into the Datastore."""
        try:
            return (bool(self.myself) if self.key and self.key.id()
                    else False)
        except Exception:
            return False

    def put(self):
        """Saving the entity into the Datastore."""
        client.put(self)
        return self.key

    def remove(self):
        """Removes current entity and its dependencies."""
        self.key.delete()

    @property
    def usafe(self):
        return self.key.urlsafe()

    @staticmethod
    def get(urlsafe):
        item = ndb.Key(
            urlsafe=urlsafe, project=settings.PROJECT_ID, namespace=NAMESPACE
        ).get()
        if not item:
            raise Exception("item doesn't exist")
        return item

    @classmethod
    def model_name(cls):
        return cls.__name__.replace("Model", "")


class EntityMixin:

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
        dest = getattr(cls, prop)
        src = getattr(self, prop)
        query = cls.query(dest == src)
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
