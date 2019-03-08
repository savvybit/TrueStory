"""RSS feed crawler capable of extracting and parsing found articles."""


import collections
import logging
import time
from datetime import datetime, timezone
from http import HTTPStatus

import feedparser
from newspaper import Article as NewsArticle

from truestory.models.article import ArticleModel


class RssCrawler:

    def __init__(self, rss_targets):
        """Instantiates with a RSS targets list to crawl."""
        self._rss_targets = rss_targets
        self._extracted_articles = collections.defaultdict(list)

    @staticmethod
    def _extract_article(feed_entry, source_name):
        """Extracts all the information needed and returns it as `ArticleModel`."""
        # Link and title are mandatory fields in a RSS. If missing, we cannot
        # parse the article.
        link = feed_entry.get("link")
        title = feed_entry.get("title")
        if not all([link, title]):
            return None

        # Get some extra info within the feed itself and using `newspaper` help.
        # The 'description' value seems to be an alternative tag for summary.
        summary = feed_entry.get("summary") or feed_entry.get("description")
        news_article = NewsArticle(link)
        news_article.download()
        news_article.parse()
        news_article.nlp()

        # Create and return article in the DB with all the gathered data.
        article_ent = ArticleModel(
            source=source_name,
            link=link,
            title=title,
            content=news_article.text,
            summary=summary,
            authors=news_article.authors,
            published=news_article.publish_date,
            img=news_article.top_image,
            categories=news_article.keywords,
        )
        return article_ent

    @staticmethod
    def _manage_status(response, target):
        """Handles some of the possible problematic statuses and updates target.

        Returns:
            bool: True if we shall crawl the target, False otherwise.
        """
        name = target.link

        # We shall never crawl it again.
        if response.status == HTTPStatus.GONE:
            logging.warning("RSS is dead for %r.", name)
            target.has_gone()
            return False

        # We should know that it requires auth and implement it in the future.
        if response.status == HTTPStatus.UNAUTHORIZED:
            logging.warning("RSS requires auth for %r.", name)
            target.needs_auth()
            return False

        # Nothing new received from it.
        if response.status == HTTPStatus.NOT_MODIFIED:
            logging.info("RSS has no data for %r.", name)
            return False

        # URL has permanently moved, so we have to update with the new one.
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
        """Filters out from feed the ones which are older than the given date.

        Returns:
            tuple: list of new entries and a new date to crawl afterwards.
        """
        # Filter current entries based on the provided modified date.
        new_entries = []
        max_date = date

        for entry in entries:
            entry_date = cls._time_to_date(entry.get("published_parsed"))
            if not max_date:
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

        # In case RSS feed doesn't support modified tag, we compute it.
        if not modified:
            response.entries, modified = cls._entries_after_date(
                response.entries, target.last_modified
            )

        return response, modified, etag

    @classmethod
    def _parse_target(cls, target):
        """Parses the given RSS target, then extracts and returns all found articles.
        """
        response, modified, etag = cls._get_recent_feed(target)

        # Bozo is a tag which tells that the RSS hasn't been parsed correctly.
        if response.bozo:
            raise Exception(response.bozo)

        articles = []
        # All good, check the status first to see if we can continue with the
        # extraction.
        if cls._manage_status(response, target):
            for feed_entry in response.entries:
                # Extracts data and saves new articles in the DB with it.
                try:
                    article = cls._extract_article(feed_entry, target.source_name)
                except Exception as exc:
                    logging.exception("Got %s while parsing %r.", exc, feed_entry.id)
                else:
                    articles.append(article)
            target.checkpoint(modified, etag)

        return articles

    def crawl_targets(self):
        """Crawls the most recent feed from all the given RSS targets."""
        if not self._rss_targets:
            logging.warning("No links provided to the crawler.")
            return

        for target in self._rss_targets:
            link = target.link
            logging.debug(
                "Crawling target URL %r for articles newer than %s.",
                link, target.last_modified
            )
            try:
                articles = self._parse_target(target)
            except Exception as exc:
                logging.exception("RSS target error with %r: %s", link, exc)
            else:
                self._extracted_articles[link].extend(articles)

        return self._extracted_articles
