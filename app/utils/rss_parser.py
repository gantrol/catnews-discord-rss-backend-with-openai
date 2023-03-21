import feedparser


def parse_rss_feed(url: str):
    feed = feedparser.parse(url)
    return feed
