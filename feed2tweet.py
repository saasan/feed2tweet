from datetime import datetime
from dateutil.parser import isoparse
import feedparser
import logging
import sys
import time
import tweepy
from settings import settings


class Feed2Tweet:
    def __init__(self) -> None:
        # ログ出力の設定
        print(__name__)
        self.logger = logging.getLogger(__name__)
        # tweepy
        self.twitter_client = None


    def twitter_authentication(self) -> None:
        """Twitterでの認証"""
        if self.twitter_client is not None: return

        try:
            self.twitter_client = tweepy.Client(
                consumer_key=settings.consumer_key,
                consumer_secret=settings.consumer_secret,
                access_token=settings.access_token,
                access_token_secret=settings.access_token_secret
            )

        except tweepy.TweepyException as e:
            self.logger.critical('エラー: Twitterの認証に失敗')
            self.logger.critical(e)
            sys.exit(1)


    def post_to_twitter(self, entry: feedparser.FeedParserDict) -> None:
        """Twitterへの投稿"""
        if self.twitter_client is None:
            self.logger.critical('エラー: Twitter未認証')
            sys.exit(1)

        try:
            tweet = entry.title[:settings.max_tweet_char] + ' ' + entry.link
            self.twitter_client.create_tweet(text=tweet)
        except tweepy.TweepyException as e:
            self.logger.critical('エラー: Twitterへの投稿に失敗')
            self.logger.critical(e)
            sys.exit(1)


    def get_tweeted(self) -> int | None:
        """ツイート済み日時の取得"""
        try:
            with open(settings.tweeted_file, 'r') as file:
                tweeted = file.read()
        except FileNotFoundError:
            tweeted = ''

        if len(tweeted) == 0:
            return None

        return int(tweeted)


    def save_tweeted(self) -> None:
        """ツイート済み日時の保存"""
        unix_time = str(int(time.time()))
        with open(settings.tweeted_file, 'w') as file:
            file.write(unix_time)


    def filter_untweeted(self, entries, tweeted: int | None):
        """未ツイートのエントリーを取得"""
        if tweeted is None:
            return entries

        return filter(lambda entry: isoparse(entry.updated).timestamp() > tweeted, entries)


    def fetch_and_post_rss(self) -> None:
        """RSSフィードの取得と投稿"""
        self.logger.info('RSSフィードの取得')
        feed = feedparser.parse(settings.feed_url)
        if 'status' not in feed or feed.status >= 400:
            self.logger.critical('エラー: RSSフィードの取得に失敗')
            sys.exit(1)

        # ツイート済み日時の取得
        tweeted: int | None = self.get_tweeted()

        if tweeted is None:
            entries = reversed(feed.entries[:settings.untweeted_max_num])
        else:
            self.logger.info('ツイート済み日時: ' + str(tweeted) + ' ' + datetime.fromtimestamp(tweeted).strftime('%Y-%m-%d %H:%M:%S'))
            entries = self.filter_untweeted(reversed(feed.entries), tweeted)

        self.logger.info('Twitterでの認証')
        self.twitter_authentication()

        self.logger.info('Twitterへの投稿')
        for entry in entries:
            self.logger.info(entry.title + ' ' + entry.link)
            self.post_to_twitter(entry)
            time.sleep(settings.tweet_interval)

        # ツイート済み日時の保存
        self.save_tweeted()
