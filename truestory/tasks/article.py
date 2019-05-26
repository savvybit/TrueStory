"""Article and bias pair related tasks."""


import datetime
import logging

from truestory.crawlers import RssCrawler
from truestory.models import ArticleModel, BiasPairModel, RssTargetModel
from truestory.tasks.util import create_task


ARTICLES_PER_TARGET = 10
ARTICLES_MAX_AGE = 2  # in days
BIAS_MIN_SCORE = 0.5  # as float percentage


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


@create_task("clean-queue")
def clean_articles():
    """Cleans all outdated articles."""
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


def _get_bias_score(main, candidate):
    """Returns a score between 0 and 1 describing how contradictory they are."""
    main_kw, candidate_kw = set(main.keywords), set(candidate.keywords)
    min_count, max_count = map(
        lambda func: func(len(main_kw), len(candidate_kw)),
        (min, max)
    )
    miss_weight = 1 / max_count / 2
    match_weight = (1 - miss_weight * (max_count - min_count)) / min_count
    common_count = len(main_kw & candidate_kw)
    score = common_count * match_weight
    return score


@create_task("bias-queue")
def pair_article(article_usafe):
    """Creates bias pairs for an article (if any found)."""
    main_article = ArticleModel.get(article_usafe)
    related_articles = {}
    for keyword in main_article.keywords:
        article_query = ArticleModel.query(("keywords", "=", keyword))
        articles = ArticleModel.all(article_query)
        for article in articles:
            related_articles[article.link] = article

    del related_articles[main_article.link]
    count = 0
    for article in related_articles.values():
        score = _get_bias_score(main_article, article)
        if score < BIAS_MIN_SCORE:
            continue

        qfilters_list = [
            (("left", "=", main_article.key), ("right", "=", article.key)),
            (("left", "=", article.key), ("right", "=", main_article.key)),
        ]
        bias_pair_keys = set()
        for qfilters in qfilters_list:
            bias_pair_query = BiasPairModel.query(*qfilters)
            bias_pairs = ArticleModel.all(
                query=bias_pair_query, keys_only=True, order=False
            )
            bias_pair_keys |= {bias_pair.key for bias_pair in bias_pairs}
        if bias_pair_keys:
            logging.info("Removing %d duplicate bias pairs first.", len(bias_pair_keys))
            BiasPairModel.remove_multi(bias_pair_keys)

        logging.info("Adding new bias pair with score %f.", score)
        BiasPairModel(left=main_article.key, right=article.key, score=score).put()
        count += 1

    return {"bias_pairs": count}
