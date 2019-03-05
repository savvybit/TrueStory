from google.cloud import datastore


class ArticleHelper(object):

    @staticmethod
    def add_article_entity(client):
        """Adds new entity of kind ArticleModel and returns it."""
        key = client.key('ArticleModel')
        article = datastore.Entity(key=key, exclude_from_indexes=('content',))

        client.put(article)

        return article
