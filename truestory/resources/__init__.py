"""All resources exposed by the TrueStory web API."""


from . import article
from .. import api


resources = [
    article.CounterArticleResource,
    article.DataArticleResource,
]


for resource in resources:
    api.add_resource(
        resource,
        resource.get_route(),
        endpoint=resource.get_endpoint()
    )
