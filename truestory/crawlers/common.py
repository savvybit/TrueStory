"""Common utilities and procedures used by any crawling technique."""


import urllib.parse as urlparse

from bs4 import BeautifulSoup


def strip_article_link(link):
    """Returns an article link without the query."""
    parsed = urlparse.urlsplit(link)
    parts = [parsed.scheme, parsed.netloc, parsed.path, None, None]
    return urlparse.urlunsplit(parts)


def strip_html(html):
    """Returns the text only out of any potential HTML content."""
    if not html:
        return html

    soup = BeautifulSoup(html, "html5lib")
    return soup.text.strip()
