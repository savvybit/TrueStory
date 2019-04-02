"""Here goes all the NDB models for persistent storage."""


from .article import ArticleModel, BiasPairModel
from .base import BaseModel, DuplicateMixin, NAMESPACE, ndb
from .mail import MailModel
from .rss import RssTargetModel
