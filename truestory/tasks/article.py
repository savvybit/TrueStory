"""Article and bias pair related tasks."""


import datetime
import logging

from truestory.crawlers import RssCrawler
from truestory.models import ArticleModel, BiasPairModel, RssTargetModel
from truestory.tasks.util import create_task


ARTICLES_PER_TARGET = 10
ARTICLES_MAX_AGE = 2  # in days


@create_task("crawl-queue")
def _crawl_articles(rss_target_usafe):
    rss_target = RssTargetModel.get(rss_target_usafe)
    rss_crawler = RssCrawler([rss_target], limit=ARTICLES_PER_TARGET)
    articles_dict = rss_crawler.crawl_targets()
    articles = sum(articles_dict.values(), [])
    count = len(articles)
    logging.info("Saving %d articles into DB.", count)
    ArticleModel.put_multi(articles)
    return {"articles": count}


def crawl_articles():
    """Crawls and saves new articles in the DB."""
    rss_targets = RssTargetModel.all(keys_only=True)
    count = len(rss_targets)
    logging.info("Starting crawling with %d targets.", count)
    for rss_target in rss_targets:
        _crawl_articles(rss_target.urlsafe)
    return {"targets": count}


def _clean_articles():
    delta = datetime.timedelta(days=ARTICLES_MAX_AGE)
    min_date = datetime.datetime.utcnow() - delta
    qfilters_list = [
        (("published", "<", min_date),),
        (("published", "=", None), ("created_at", "<", min_date)),
    ]
    article_keys = set()
    for qfilters in qfilters_list:
        article_query = ArticleModel.query(*qfilters)
        articles = ArticleModel.all(query=article_query, keys_only=True, order=False)
        article_keys |= {article.key for article in articles}
    articles_count = len(article_keys)

    logging.debug("Collecting bias pairs for removal of %d articles.", articles_count)
    bias_pairs = BiasPairModel.query().fetch()
    bias_pairs = filter(
        lambda pair: pair.left in article_keys or pair.right in article_keys,
        bias_pairs
    )
    bias_pair_keys = [bias_pair.key for bias_pair in bias_pairs]
    bias_pairs_count = len(bias_pair_keys)

    logging.info("Removing %d bias pairs.", bias_pairs_count)
    BiasPairModel.remove_multi(bias_pair_keys)
    logging.info("Removing %d articles.", articles_count)
    ArticleModel.remove_multi(article_keys)
    return {"bias_pairs": bias_pairs_count, "articles": articles_count}


@create_task("clean-queue")
def clean_articles():
    """Cleans all outdated articles."""
    return _clean_articles()
