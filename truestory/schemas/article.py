"""Handles article related objects (de)serialization."""


from truestory import api, ma
from truestory.resources.article import DataArticleResource


class ArticleSchema(ma.Schema):

    class Meta:
        fields = ("source_name", "link", "title", "image", "url")
        ordered = True

    _endpoint = f"{api.app.name}.{DataArticleResource.get_endpoint()}"
    url = ma.AbsoluteURLFor(_endpoint, article_usafe="<urlsafe>")


article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True, only=("url",))
