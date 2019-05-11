"""RSS feed crawler capable of extracting and parsing found articles."""


import collections
import logging
import time
from datetime import datetime, timezone
from http import HTTPStatus

import feedparser

from truestory.functions import parse_article
from truestory.models.article import ArticleModel


class RssCrawler:

    def __init__(self, rss_targets, limit=None):
        """Instantiates with a RSS target list to crawl.

        Args:
            rss_targets (list): List of `RssTargetModel` objects.
            limit (int): How many results to crawl within each target.
        """
        self._rss_targets = rss_targets
        self._limit = limit

    @staticmethod
    def _extract_article(feed_entry, source_name):
        """Extracts all the information needed from a `feed_entry` and returns it as
        an `ArticleModel` object.
        """
        # Link and title are mandatory fields in a RSS. If missing, we cannot
        # parse the article.
        link = feed_entry.get("link")
        title = feed_entry.get("title")
        if not all([link, title]):
            raise KeyError("link or title missing from the article")

        # The 'description' value seems to be an alternative tag for summary.
        summary = feed_entry.get("summary") or feed_entry.get("description")
        news_article = parse_article.get_article(link)

        article_ent = ArticleModel(
            source_name=source_name,
            link=link,
            title=title,
            content=news_article.text,
            summary=summary,
            authors=news_article.authors,
            published=news_article.publish_date or None,
            image=news_article.top_image,
            keywords=news_article.keywords,
        )
        return article_ent

    @staticmethod
    def _manage_status(response, target):
        """Handles some of the possible problematic feed statuses and updates `target`
        accordingly.

        Returns:
            bool: True if we can crawl the target, False otherwise.
        """
        name = target.link

        # We shall never crawl it again.
        if response.status == HTTPStatus.GONE:
            logging.warning("RSS is dead for %r.", name)
            target.has_gone()
            return False

        # Becomes aware that it requires auth and must support it in the future.
        if response.status == HTTPStatus.UNAUTHORIZED:
            logging.warning("RSS requires auth for %r.", name)
            target.needs_auth()
            return False

        # Nothing new received from it.
        if response.status == HTTPStatus.NOT_MODIFIED:
            logging.info("RSS has no data for %r.", name)
            return False

        # URL has permanently moved, so we have to update target with the new one.
        if response.status == HTTPStatus.MOVED_PERMANENTLY:
            logging.info("RSS has moved for %r.", name)
            target.moved_to(response.href)

        return True

    @staticmethod
    def _time_to_date(parsed_time):
        """Converts `parsed_time` to a datetime object."""
        if not parsed_time:
            return parsed_time
        return datetime.fromtimestamp(time.mktime(parsed_time), tz=timezone.utc)

    @classmethod
    def _entries_after_date(cls, entries, date):
        """Filters the `entries` which are older than the given `date`.

        Returns:
            tuple: A list of new entries and a new date to crawl afterwards.
        """
        new_entries = []
        max_date = date

        for entry in entries:
            entry_date = cls._time_to_date(entry.get("published_parsed"))
            if not max_date:
                # `max_date` could be None if target's last modified date is not
                # initialized yet.
                max_date = entry_date
            if all([entry_date, date]) and entry_date <= date:
                continue

            new_entries.append(entry)
            if entry_date and entry_date > max_date:
                max_date = entry_date

        return new_entries, max_date

    @classmethod
    def _get_recent_feed(cls, target):
        """Retrieves the RSS feed through `feedparser` and updates the timestamp of
        the last retrieval in order to avoid getting banned or having duplicate data.

        Returns:
            tuple: Article, its modified date and the e-tag.
        """
        response = feedparser.parse(
            target.link, modified=target.last_modified, etag=target.etag
        )

        # Some of the feeds offer one of these two tags and others none of them.
        modified = cls._time_to_date(response.get("modified_parsed"))
        etag = response.get("etag")

        # In case RSS feed doesn't support modified tag, we compute it artificially.
        if not modified:
            response.entries, modified = cls._entries_after_date(
                response.entries, target.last_modified
            )

        return response, modified, etag

    def _extract_articles(self, target):
        """Parses the given RSS target, then extracts and returns all found articles.
        """
        feed_response, modified, etag = self._get_recent_feed(target)

        # Bozo is a tag which tells that the RSS hasn't been parsed correctly.
        if feed_response.bozo:
            raise Exception(feed_response.bozo)

        articles = []
        count = 0
        if self._manage_status(feed_response, target):
            for feed_entry in feed_response.entries:
                if self._limit and count >= self._limit:
                    logging.info(
                        "Crawling limit of %d article(s) was reached for this target.",
                        count
                    )
                    break
                try:
                    article = self._extract_article(feed_entry, target.source_name)
                except Exception as exc:
                    logging.exception("Got %s while parsing %r.", exc, feed_entry.id)
                else:
                    articles.append(article)
                    count += 1
            target.checkpoint(modified, etag)

        return articles

    def crawl_targets(self):
        """Crawls the most recent feed from each of the given RSS targets.

        Returns:
            dict: A list of articles by each target URL.
        """
        extracted_articles = collections.defaultdict(list)

        if not self._rss_targets:
            logging.warning("No targets available, check database.")
            return extracted_articles

        for target in self._rss_targets:
            link = target.link
            logging.debug(
                "Crawling target URL %r for articles newer than %s.",
                link, target.last_modified
            )
            try:
                articles = self._extract_articles(target)
            except Exception as exc:
                logging.exception("RSS target error with %r: %s", link, exc)
            else:
                extracted_articles[link].extend(articles)

        return extracted_articles
