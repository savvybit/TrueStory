from google.cloud import datastore


class RssTargetHelper(object):

    @staticmethod
    def add_rss_target(client, link, name):
        """Adds new rss target with given data."""
        key = client.key('RssTargetModel')
        rss_target = datastore.Entity(key=key, exclude_from_indexes=['link'])
        rss_target.update({
            'link': link,
            'source_name': name,
            'auth_required': False
        })

        client.put(rss_target)

        return rss_target.id

    @staticmethod
    def update_target_date(client, target, modified, etag):
        """Updates the hour of last crawling of the target."""
        with client.transaction():
            rss_target = client.get(target.key)

            if not rss_target:
                raise ValueError(
                    'Rss target {} does not exist.'.format(id))

            rss_target.last_modified = modified
            rss_target.etag = etag

            client.put(rss_target)

    @staticmethod
    def delete_target(client, target):
        """Deletes the given target"""
        key = client.key('RssTargetModel', target.id)
        client.delete(key)

    @staticmethod
    def list_rss_targets(client):
        """Returns a list of all entries of RssTargetModel kind."""
        query = client.query(kind='RssTargetModel')

        return list(query.fetch())

    @staticmethod
    def mark_auth_required(client, target):
        """Sets that auth is required for the target."""
        with client.transaction():
            target.auth_required = True

            client.put(target)

    @staticmethod
    def update_target_link(client, target, href):
        """Updates the link for the target."""
        with client.transaction():
            target['link'] = href

            client.put(target)


