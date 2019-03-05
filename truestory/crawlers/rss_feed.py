import logging
from time import mktime
from datetime import datetime

import feedparser as fd
from newspaper import Article

from truestory.models import ArticleModel
from truestory.crawlers.rss_target_helper import RssTargetHelper
from truestory.crawlers.article_helper import ArticleHelper

from google.cloud import datastore
from truestory.models import ndb

# Describes status codes returned by feedparser
TEMPORARY_MOVED = 302
PERMANENTLY_MOVED = 301
NO_DATA = 304
DELETED = 410
PASSWORD_PROTECTED = 401


class RssCrawler(object):

    @staticmethod
    def crawl_links(client, rss_targets):
        """Crawls the recent feed of all the rss targets given."""
        if not rss_targets:
            logging.info('No links provided to the crawler.')

        for target in rss_targets:
            RssCrawler.parse_target(client, target)

    @staticmethod
    def last_modified_date(entries):
        """Computes the most recent date of the crawled articles of the feed."""
        publish_dates = [entry.get('published_parsed') for entry in entries]

        if len(publish_dates) > 0:
            return max(publish_dates)

        return None

    @staticmethod
    def entries_after_date(entries, date):
        """Filters out from feed the ones who are older than given date."""
        filtered_entries = []

        for entry in entries:
            if entry.get('published_parsed') > date:
                filtered_entries.append(entry)

        return filtered_entries

    @staticmethod
    def recent_feed(rss_link, modified, etag):
        """Retrieves the rss feed through feedparser and updates time of the
        last retrieval to avoid getting banned or having duplicate data.
        """
        response = fd.parse(
            rss_link, modified=modified, etag=etag)

        # Some of the feeds offer one of these two tags and some none.
        modified = response.get('modified', None)
        etag = response.get('etag', None)

        # In case rss feed doesn't support modified tag, we compute it.
        if not modified:
            modified_time = RssCrawler.last_modified_date(response.entries)
            response.entries = \
                RssCrawler.entries_after_date(response.entries, modified_time)

            modified = datetime.fromtimestamp(mktime(modified_time))

        return response, modified, etag

    @staticmethod
    def manage_status(client, response, target):
        """Handles some of the possible errors status and updates target.
        Returns True if we shall crawl the target.
        """

        # We shall never crawl it again.
        if response.status == DELETED:
            logging.info('[RSS] Deleted ' + target.link)
            RssTargetHelper.delete_target(client, target)
            return False

        # We should know that it requires auth and implement it further.
        elif response.status == PASSWORD_PROTECTED:
            logging.info('[RSS] Password protected ' + target.link)
            RssTargetHelper.mark_auth_required(client, target)
            return False

        elif response.status == NO_DATA:
            logging.info('[RSS] No data for ' + target.link)
            return False

        # Link has permanently moved, so we have to update the ds entry
        elif response.status == PERMANENTLY_MOVED:
            RssTargetHelper.update_target_link(client, target, response.href)

        return True

    @staticmethod
    def extract_article_data(feed_entry, source_name):
        """Extracts all information needed for article model."""

        # Link and title are mandatory fields in a RSS. If missing, we cannot
        # parse the article
        if not feed_entry.get('link') or not feed_entry.get('title'):
            return None

        article_data = ArticleModel(
            title=feed_entry.get('title'),
            link=feed_entry.get('link'),
            summary=feed_entry.get('summary'),
            source=source_name
        )

        # 'Description' seems to be an alternative tag for summary.
        if not article_data.summary:
            article_data.summary = feed_entry.get('description')

        # If these tags are missing, we parse the article itself to get them.
        if not article_data.content or not article_data.img:

            article = Article(article_data.link)
            article.download()
            article.parse()

            article_data.content = article.text
            article_data.img = article.top_image
            article_data.authors = article.authors
            article_data.published = article.publish_date

            article.nlp()
            article_data.categories = article.keywords

        return article_data

    @staticmethod
    def parse_target(client, target):
        """Parses the rss link given and extracts articles data."""
        response, modified, etag = RssCrawler.recent_feed(
            target.link, target.last_modified, target.etag)

        # Bozo is a tag which warns that the rss hasn't been parsed correctly.
        if response.bozo:
            logging.info('[RSS] Bozo error in link ' + target.link)

        # We need a status to parse the feed. If missing, an error has occured.
        if 'status' in response:

            if RssCrawler.manage_status(client, response, target):

                for feed_entry in response.get('entries'):
                    # Extract all needed data to fill in the article model.
                    data = RssCrawler.extract_article_data(
                        feed_entry, target.source_name)
                    if data:
                        article = ArticleHelper.add_article_entity(client)
                        article.update(data.to_dict())
                        client.put(article)

                # As we just parsed a target, we update date metadata.
                RssTargetHelper.update_target_date(client, target, modified, etag)


def main():
    client = datastore.Client(project='truestory', namespace='development')
    ndb.enable_use_with_gcd(client.project)

    rss_list = RssTargetHelper.list_rss_targets(client)
    RssCrawler.crawl_links(client, rss_list)


if __name__ == "__main__":
    main()
