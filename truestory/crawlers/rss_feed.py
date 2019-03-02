import logging

import feedparser as fd

from truestory.models import ArticleModel


TEMPORARY_MOVED = 302
PERMANENTLY_MOVED = 301
NO_DATA = 304
DELETED = 410
PASSWORD_PROTECTED = 401


class RssCrawler(object):

    @staticmethod
    def crawl_links(rss_targets):
        if not rss_targets:
            logging.info('No links provided to the crawler.')

        for target in rss_targets:
            RssCrawler.parse_target(target)

    @staticmethod
    def last_modified_date(entries):
        publish_dates = [entry.get('published_parsed') for entry in entries]

        if len(publish_dates) > 0:
            return max(publish_dates)

        return None

    @staticmethod
    def entries_after_date(entries, date):
        filtered_entries = []

        for entry in entries:
            if entry.get('published_parsed') > date:
                filtered_entries.append(entry)

        return filtered_entries

    @staticmethod
    def recent_feed(rss_link, modified, etag):

        response = fd.parse(
            rss_link, modified=modified, etag=etag)

        modified = response.get('modified', None)
        etag = response.get('etag', None)

        if not modified:
            modified = RssCrawler.last_modified_date(response.entries)
            response.entries = RssCrawler.entries_after_date(response, modified)

        return response, modified, etag

    @staticmethod
    def update_target(target, modified, etag, new_href=None):

        if new_href:
            target.link = new_href

        target.last_modified = modified
        target.etag = etag

        # target.put()
        print(target)

    @staticmethod
    def parse_target(target):

        response, modified, etag = RssCrawler.recent_feed(
            target.link, target.last_modified, target.etag)

        if response.status == DELETED:
            logging.info('[RSS] Deleted ' + target.link)
            target.key.delete()

        elif response.status == PASSWORD_PROTECTED:
            logging.info('[RSS] Password protected ' + target.link)

        elif response.status == NO_DATA:
            logging.info('[RSS] No data for ' + target.link)

        else:

            RssCrawler.update_target(
                modified,
                etag,
                response.href if response.status == PERMANENTLY_MOVED else None)

            for feed_entry in response.entries:

                article = ArticleModel(
                    title=feed_entry.title,
                    link=feed_entry.link,
                    published=feed_entry.published,
                    id=feed_entry.id,
                    summary=feed_entry.summary,
                    language=feed_entry.content.language,
                    content=feed_entry.content.value
                )
                # article.put()

                print(article)


def main():
    from truestory.models import RssTargetModel

    test_link = RssTargetModel(
        link="http://feeds.feedburner.com/TechCrunch/"
    )

    rss_list = [test_link]

    RssCrawler.crawl_links(rss_list)


if __name__ == "__main__":
    main()
