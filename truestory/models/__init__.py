"""Here goes all the NDB models for persistent storage."""


from .article import ArticleModel
from .base import BaseModel, EntityMixin, StatusMixin, client, ndb
from .rss_target import RssTargetModel
