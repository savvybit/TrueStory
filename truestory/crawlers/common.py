"""Common utilities and procedures used by any crawling technique."""


import urllib.parse as urlparse

from bs4 import BeautifulSoup


ALLOWED_QUERY_PARAMS = {"id",}


def strip_article_link(link, site=None):
    """Returns an article link without the query."""
    parsed = urlparse.urlsplit(link)

    netloc = parsed.netloc
    if site and site not in link:
        netloc = site

    query = dict(urlparse.parse_qsl(parsed.query))
    for key in set(query.keys()) - ALLOWED_QUERY_PARAMS:
        del query[key]
    query_str = urlparse.urlencode(query)

    parts = [parsed.scheme, netloc, parsed.path, query_str, None]
    return urlparse.urlunsplit(parts)


def strip_html(html):
    """Returns the text only out of any potential HTML content."""
    if not html:
        return html

    soup = BeautifulSoup(html, "html5lib")
    return soup.text.strip()
