"""Article and bias pair related tasks."""


import logging

from truestory.crawlers import RssCrawler
from truestory.models import ArticleModel, RssTargetModel
from truestory.tasks.util import create_task


ARTICLES_PER_TARGET = 10


@create_task("crawl-queue")
def _crawl_articles(rss_target_usafe):
    rss_target = RssTargetModel.get(rss_target_usafe)
    rss_crawler = RssCrawler([rss_target], limit=ARTICLES_PER_TARGET)
    articles_dict = rss_crawler.crawl_targets()
    articles = sum(articles_dict.values(), [])
    count = len(articles)
    logging.info("Saving %d articles into DB.", count)
    ArticleModel.put_multi(articles)
    return count


def crawl_articles():
    """Crawls and saves new articles in the DB."""
    rss_targets = RssTargetModel.all(keys_only=True)
    count = len(rss_targets)
    logging.info("Starting crawling with %d targets.", count)
    for rss_target in rss_targets:
        _crawl_articles(rss_target.urlsafe)
    return count
