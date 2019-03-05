from google.cloud import datastore


def add_rss_link(link):
    key = client.key('Test')

    rss_target = datastore.Entity(
        key, exclude_from_indexes=['link'])

    rss_target.update({
        'link': link,
        'auth_required': False
    })

    client.put(rss_target)

    return rss_target.id


def mark_auth_required(id):
    with client.transaction():
        key = client.key('Test', id)
        rss_target = client.get(key)

        if not rss_target:
            raise ValueError(
                'Rss target {} does not exist.'.format(id))

        rss_target['auth_required'] = True

        client.put(rss_target)


def delete_rss_target(id):
    key = client.key('Test', id)
    client.delete(key)


def list_rss_targets():
    query = client.query(kind='Test')

    return list(query.fetch())


if __name__ == "__main__":
    client = datastore.Client(project='truestory', namespace='development')
    rid = add_rss_link('http://feeds.feedburner.com/TechCrunch/')
    mark_auth_required(rid)
    print(list_rss_targets())
    delete_rss_target(rid)
    print(list_rss_targets())
