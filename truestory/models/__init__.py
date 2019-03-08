"""Here goes all the NDB models for persistent storage."""


from .article import ArticleModel
from .base import BaseModel, DuplicateMixin, ndb
from .rss import RssTargetModel
