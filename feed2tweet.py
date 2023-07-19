from datetime import datetime
from dateutil.parser import isoparse
from misskey import Misskey
from misskey.exceptions import MisskeyAPIException, MisskeyAuthorizeFailedException
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
        # misskey
        self.misskey_client = None


    def initialize_twitter_client(self) -> None:
        """Twitterクライアントの初期化"""
        if self.twitter_client is not None: return

        try:
            self.twitter_client = tweepy.Client(
                consumer_key=settings.consumer_key,
                consumer_secret=settings.consumer_secret,
                access_token=settings.access_token,
                access_token_secret=settings.access_token_secret
            )

        except tweepy.TweepyException as e:
            self.logger.critical('エラー: Twitterクライアントの初期化に失敗')
            self.logger.critical(e)
            sys.exit(1)


    def initialize_misskey_client(self) -> None:
        """Misskeyクライアントの初期化"""
        if self.misskey_client is not None: return
        if settings.misskey_address is None or settings.misskey_token is None: return

        try:
            self.misskey_client = Misskey(settings.misskey_address, i=settings.misskey_token)

        except (MisskeyAPIException, MisskeyAuthorizeFailedException) as e:
            self.logger.critical('エラー: Misskeyクライアントの初期化に失敗')
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
            if len(e.api_messages) > 0 and e.api_messages[0] == 'You are not allowed to create a Tweet with duplicate content.':
                self.logger.info('ツイート内容重複のためスキップ')
            else:
                self.logger.critical('エラー: Twitterへの投稿に失敗')
                self.logger.critical(e)
                sys.exit(1)


    def post_to_misskey(self, entry: feedparser.FeedParserDict) -> None:
        """Misskeyへの投稿"""
        if self.misskey_client is None: return

        try:
            tweet = entry.title[:settings.max_tweet_char] + ' ' + entry.link
            self.misskey_client.notes_create(text=tweet)
        except (MisskeyAPIException, MisskeyAuthorizeFailedException) as e:
            self.logger.critical('エラー: Misskeyへの投稿に失敗')
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

        self.logger.info('Twitterクライアントの初期化')
        self.initialize_twitter_client()

        self.logger.info('Misskeyクライアントの初期化')
        self.initialize_misskey_client()

        self.logger.info('Twitter/Misskeyへの投稿')
        for entry in entries:
            self.logger.info(entry.title + ' ' + entry.link)
            self.post_to_twitter(entry)
            self.post_to_misskey(entry)
            time.sleep(settings.tweet_interval)

        # ツイート済み日時の保存
        self.save_tweeted()
