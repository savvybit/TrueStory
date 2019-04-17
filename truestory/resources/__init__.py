"""All resources exposed by the TrueStory web API."""


from . import article
from .. import api


resources = [
    article.CounterArticleResource,
]


for resource in resources:
    api.add_resource(
        resource,
        resource.get_route(),
        endpoint=resource.ENDPOINT
    )
