import sys

from google.cloud import datastore

from truestory.crawlers.rss_feed import RssCrawler
from truestory.models import RssTargetModel


client = None


def add_rss_link(link):
    key = client.key("Test")

    rss_target = datastore.Entity(
        key, exclude_from_indexes=["link"])

    rss_target.update({
        "link": link,
        "auth_required": False
    })

    client.put(rss_target)

    return rss_target.id


def mark_auth_required(id):
    with client.transaction():
        key = client.key("Test", id)
        rss_target = client.get(key)

        if not rss_target:
            raise ValueError(
                "Rss target {} does not exist.".format(id))

        rss_target["auth_required"] = True

        client.put(rss_target)


def delete_rss_target(id):
    key = client.key("Test", id)
    client.delete(key)


def list_rss_targets():
    query = client.query(kind="Test")

    return list(query.fetch())


def add_remove_rss():
    rid = add_rss_link("http://feeds.feedburner.com/TechCrunch/")
    mark_auth_required(rid)
    print(list_rss_targets())
    delete_rss_target(rid)
    print(list_rss_targets())


def rss_feed():
    rss_targets = RssTargetModel.all()
    crawler = RssCrawler(rss_targets)
    articles = crawler.crawl_targets()
    print(articles)


def test_model():
    target = RssTargetModel(source_name="test")
    target.put()


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} FUNC")
        return

    global client
    client = datastore.Client(project="truestory", namespace="development")

    funcs = {
        "rss": add_remove_rss,
        "rss_feed": rss_feed,
        "test_model": test_model,
    }
    funcs[sys.argv[1]]()


if __name__ == "__main__":
    main()

# Example: $ python dstore.py rss_feed
