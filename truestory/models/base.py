"""Base models and utilities used by the derived ones."""


import datetime
import logging

import ndb_orm as ndb
from google.cloud import datastore

from truestory import settings


# Root key values. Makes the DB strongly consistent.
KEY_KIND = settings.APP_NAME
KEY_ID = 1

client = datastore.Client()
ndb.enable_use_with_gcd(client.project)


def get_root_key():
    return ndb.Key(KEY_KIND, KEY_ID)


class BaseModel(ndb.Model):

    """Common model properties and functionality."""

    # String used for properties with not available data.
    NOT_SET = "N/A"

    # List of properties that are not changed automatically in case of an update. The
    # caller needs to explicitly specify them through the `change` argument.
    READ_ONLY = []
    # List of properties that shouldn't be cloned.
    CLONE_SKIP = [
        "date",
    ]

    date = ndb.DateTimeProperty(auto_now_add=True)
    parent_key = ndb.KeyProperty()

    def __init__(self, *args, parent=get_root_key(), **kwargs):
        # Continue the initialization with custom `parent` if not provided.
        super().__init__(*args, parent=parent, **kwargs)
        # Save the default/provided parent also in a property.
        self.parent_key = parent

    @classmethod
    def query(cls, *args, ancestor=get_root_key(), parent=None, **kwargs):
        # Query direct descendants if `parent` is specified.
        if parent:
            # Search for direct descendants.
            args = (cls.parent_key == parent,) + tuple(args)
        query = super().query(*args, ancestor=ancestor, **kwargs)
        return query

    @classmethod
    def all(cls, query=None, **kwargs):
        query = query or cls.query()
        return query.order(-cls.date).fetch(**kwargs)

    @classmethod
    def norm(cls, value):
        if value is None:
            return cls.NOT_SET
        return value

    @property
    def exists(self):
        """Checks if the entity is saved into the Datastore."""
        try:
            return (bool(self.myself) if self.key and self.key.id()
                    else False)
        except Exception:
            return False

    @property
    def myself(self):
        """Return the current DB version of the same object (without caching)."""
        return self.key.get(use_cache=False, use_memcache=False)

    @classmethod
    def _get_constants_set(cls, name):
        attrs = set()
        for class_ in cls.__mro__:
            constants = getattr(class_, name, None)
            if constants:
                for attr in constants:
                    attrs.add(attr)
        return attrs

    @classmethod
    def constant_read_only(cls):
        return cls._get_constants_set("READ_ONLY")

    @classmethod
    def constant_clone_skip(cls):
        return cls._get_constants_set("CLONE_SKIP")

    def put(self, if_exists=False, change=None, **kwargs):
        """Saving the entity into the Datastore using tweaks."""
        exists = self.exists

        # Save it only if it already exists.
        if if_exists and not exists:
            # Nothing added, therefore no key available for returning.
            return None

        # Now compute what to keep from the DB old values.
        if exists:
            keep = self.constant_read_only() - set(change or [])
            if keep:
                myself = self.myself
                for prop in keep:
                    value = getattr(myself, prop)
                    setattr(self, prop, value)

        # FIXME(cmiN): Make sure we return the newly created key instead.
        return client.put(self)

    def remove(self):
        """Removes current entity and its dependencies."""
        self.key.delete()

    def to_dict(self, *args, **kwargs):
        """Returns a dictionary without the skipped properties."""
        properties = super().to_dict(*args, **kwargs)
        for skip in self.constant_clone_skip():
            properties.pop(skip, None)
        return properties

    def clone(self, **kwargs):
        """Clones the current entity without the auto add properties."""
        # Retrieve all properties as they are except the skipped ones.
        properties = self.to_dict()
        # Update with the explicitly provided new ones.
        properties.update(kwargs)
        # Return a new instance of the very same class with the latest
        # properties.
        clone = type(self)(**properties)
        return clone

    @property
    def parent(self):
        return self.key.parent() if self.key else self.parent_key

    @property
    def usafe(self):
        return self.key.urlsafe()

    @staticmethod
    def get(urlsafe):
        item = ndb.Key(urlsafe=urlsafe).get()
        if not item:
            raise Exception("item doesn't exist")
        return item

    @classmethod
    def model_name(cls):
        return cls.__name__.replace("Model", "")


class StatusMixin(BaseModel):

    """Adds statuses to entities supposed to do work (crons)."""

    READ_ONLY = [
        "status",
        "status_message",
    ]
    __CHANGE = [
        "status",
        "status_message",
    ]

    # These should be overridden with custom properties depending on the implemented
    # model.
    status = ndb.IntegerProperty()
    status_message = ndb.StringProperty()

    def _set_status(self, status, message=""):
        self.status = status
        self.status_message = str(message)  # make sure it's a string
        self.put(if_exists=True, change=self.__CHANGE)


class EntityMixin(BaseModel):

    """Adds support for updating same entities when similar ones are added."""

    @classmethod
    def primary_key(cls):
        """Returns the property name holding unique values."""
        raise NotImplementedError(
            f"{cls.model_name()} primary key not specified"
        )

    def _update(self, entity, **kwargs):
        """Update itself without creating history."""
        # Update the old entity with the newly extracted values (from self).
        properties = self.to_dict()  # without the skips ofc
        # Make sure we put the current date.
        properties["date"] = datetime.datetime.utcnow()
        # Populate the original existing entity with all the non skip-able properties.
        entity.populate(**properties)
        # Save all the new incoming changes into the old entity.
        return entity.put(**kwargs)

    def get_existing(self, parent):
        """Returns already existing entity keys based on the given `parent`.

        An existing entity is one that has the same primary key attribute as the
        candidate's one.
        """
        cls = type(self)
        prop = cls.primary_key()
        dest = getattr(cls, prop)
        src = getattr(self, prop)
        query = cls.query(
            dest == src,
            parent=parent
        )
        keys = self.all(query=query, keys_only=True)
        return keys

    def put(self, parent=get_root_key(), **kwargs):
        """Check if already existing and if yes, replace the old values."""
        # Uniqueness by an ID property constraint for every extracted entity,
        # excluding the history ones if any (clones which are having the original
        # entity as `parent`).
        keys = self.get_existing(parent)

        if self.exists or not keys or self.parent != parent:
            # Save the newly extracted entity or the already present one.
            return super().put(**kwargs)

        # Just update the already existing entity and preserve history,
        # without saving a new one (clone).
        entity_id = getattr(self, self.primary_key())
        logging.debug("Updating already existing entity: %s.", entity_id)
        entity = keys[0].get(use_cache=False)
        return self._update(entity, parent=parent, **kwargs)
