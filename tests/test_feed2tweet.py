from dateutil.parser import isoparse
from unittest import mock, TestCase
import feedparser
import json
import logging
import logging.config
from feed2tweet import Feed2Tweet
from settings import settings


def post_to_twitter_dev(entry: feedparser.FeedParserDict) -> None:
    """Twitterへの投稿"""
    print(entry.title)
    print(entry.link)
    print(entry.updated)
    print(isoparse(entry.updated).strftime('%Y-%m-%d %H:%M:%S'))
    print(isoparse(entry.updated).timestamp())


def post_to_misskey_dev(entry: feedparser.FeedParserDict) -> None:
    """Misskeyへの投稿"""
    post_to_twitter_dev(entry)


def setup_logger(name: str) -> logging.Logger:
    """ログ出力の設定"""
    with open(settings.logging_config_file, encoding='utf-8') as f:
        logging_config = json.load(f)
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(name)

    return logger


class TestFeed2Tweet(TestCase):
    def test_fetch_and_post_rss(self):
        setup_logger(__name__)
        feed2tweet = Feed2Tweet()

        feed2tweet.post_to_twitter = mock.Mock(side_effect=post_to_twitter_dev)
        feed2tweet.post_to_misskey = mock.Mock(side_effect=post_to_misskey_dev)
        feed2tweet.fetch_and_post_rss()


if __name__ == '__main__':
    unittest.main()
