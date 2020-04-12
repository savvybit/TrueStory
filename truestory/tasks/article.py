"""Article and bias pair related tasks."""


import datetime
import logging
import operator

import redis_lock

from truestory import algo
from truestory.crawlers import RssCrawler
from truestory.misc import get_redis_client
from truestory.models import ArticleModel, BiasPairModel, RssTargetModel
from truestory.models.base import key_to_urlsafe, urlsafe_to_key
from truestory.tasks.util import create_task


ARTICLES_PER_TARGET = 10
ARTICLES_MAX_AGE = 2  # as days

shorten_source = lambda src_name: src_name.split("-")[0].strip()
redis_client = get_redis_client()


@create_task("crawl-queue")
def _crawl_articles(rss_target_usafe):
    rss_target = RssTargetModel.get(rss_target_usafe)
    rss_crawler = RssCrawler([rss_target], limit=ARTICLES_PER_TARGET)
    articles_dict = rss_crawler.crawl_targets()
    articles = sum(articles_dict.values(), [])
    count = len(articles)
    logging.info("Saving %d articles into DB.", count)
    article_keys = ArticleModel.put_multi(articles)
    for article_key in article_keys:
        pair_article(key_to_urlsafe(article_key))
    return {"articles": count}


def crawl_articles():
    """Crawls and saves new articles in the DB."""
    rss_targets = RssTargetModel.all(
        RssTargetModel.query(("enabled", "=", True)),
        keys_only=True
    )
    count = len(rss_targets)
    logging.info("Starting crawling with %d targets.", count)
    for rss_target in rss_targets:
        _crawl_articles(rss_target.urlsafe)
    return {"targets": count}


def _get_matching_keys(*query_filters_list, model):
    """Returns all the keys matching any of the `query_filters` given `model`."""
    entity_keys = set()
    for query_filters in query_filters_list:
        query = model.query(*query_filters)
        entities = model.all(query=query, keys_only=True, order=False)
        entity_keys |= {entity.key for entity in entities}
    return entity_keys


@create_task("clean-queue")
def _clean_article_biases(article_usafe):
    article_key = urlsafe_to_key(article_usafe, model=ArticleModel)
    logging.debug(
        "Collecting bias pairs for removal of expired article key: %s", article_key
    )

    query_filters_list = [
        (("left", "=", article_key),),
        (("right", "=", article_key),),
    ]
    bias_pair_keys = _get_matching_keys(*query_filters_list, model=BiasPairModel)

    bias_pairs_count = len(bias_pair_keys)
    logging.debug("Removing %d bias pairs.", bias_pairs_count)
    BiasPairModel.remove_multi(bias_pair_keys)
    return {"bias_pairs": bias_pairs_count}


def clean_articles():
    """Cleans all outdated articles."""
    delta = datetime.timedelta(days=ARTICLES_MAX_AGE)
    min_date = datetime.datetime.utcnow() - delta
    logging.info("Collecting articles older than %s for removal...", min_date)

    query_filters_list = [
        (("published", "<", min_date),),
        (("published", "=", None), ("created_at", "<", min_date)),
    ]
    article_keys = _get_matching_keys(*query_filters_list, model=ArticleModel)

    for article_key in article_keys:
        _clean_article_biases(key_to_urlsafe(article_key))

    articles_count = len(article_keys)
    logging.info("Removing %d articles.", articles_count)
    ArticleModel.remove_multi(article_keys)
    return {"articles": articles_count}


@create_task("bias-queue")
def pair_article(article_usafe):
    """Creates bias pairs for an article (if any found)."""
    try:
        main_article = ArticleModel.get(article_usafe)
    except Exception as exc:
        # NOTE(cmiN): Very often the article might get removed during pairing, for
        #  clean-up reasons.
        logging.exception(exc)
        return {"bias_pairs": 0}

    assert main_article.side is not None, "attempted to pair article with missing side"

    main_source_name = shorten_source(main_article.source_name)
    related_articles = {}
    for keyword in main_article.keywords:
        article_query = ArticleModel.query(("keywords", "=", keyword))
        articles = ArticleModel.all(article_query, order=False)
        for article in articles:
            if shorten_source(article.source_name) != main_source_name:
                related_articles[article.link] = article

    related_articles.pop(main_article.link, None)
    for link, article in list(related_articles.items()):
        if article.side is None:
            logging.warning(
                "Skipping related article %r because its side is missing.", link
            )
            del related_articles[link]

    added_pairs = 0
    for article in related_articles.values():
        must_save, score = algo.get_bias_score(main_article, article)
        if not must_save:
            logging.debug(
                "Skipping potential pair article %r because score is too low.",
                article.link
            )
            continue

        query_filters_list = [
            (("left", "=", main_article.key), ("right", "=", article.key)),
            (("left", "=", article.key), ("right", "=", main_article.key)),
        ]
        lock_name = "-".join(sorted(
            map(key_to_urlsafe, [main_article.key, article.key])
        ))

        with redis_lock.Lock(redis_client, lock_name):
            bias_pair_keys = _get_matching_keys(
                *query_filters_list, model=BiasPairModel
            )
            if bias_pair_keys:
                logging.info(
                    "Removing %d duplicate bias pairs first.", len(bias_pair_keys)
                )
                BiasPairModel.remove_multi(bias_pair_keys)

            articles = sorted([main_article, article], key=operator.attrgetter("side"))
            logging.info(
                "Adding new bias pair with score %f between %r and %r.",
                score, articles[0].link, articles[1].link
            )
            BiasPairModel(
                left=articles[0].key, right=articles[1].key, score=score
            ).put()
            added_pairs += 1

    return {"bias_pairs": added_pairs}
