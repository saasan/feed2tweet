import calendar
import os
import sys
import time
import feedparser
import tweepy
import redis


# RSSフィードのURL
FEED_URL = os.environ['FEED_URL']
# Twitter API Key
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
# Twitter API Secret Key
TWITTER_API_SECRET_KEY = os.environ['TWITTER_API_SECRET_KEY']
# Twitter Access Token
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
# Twitter Access Token Secret
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
# データを保存するRedisのURL
REDIS_URL = os.environ['REDIS_URL']

# ツイート済みエントリーの日時を書き込むキー名
REDIS_KEY_TWEETED = 'tweeted'
# ツイート済みエントリーの日時が保存されていない場合にツイートする最大数
UNTWEETED_MAX_NUM = 3
# URLを除いたツイートの最大文字数
MAX_TWEET_CHAR = 128


def twitter_authentication(api_key, api_secret_key, access_token, access_token_secret):
    """Twitterで認証する"""
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    return api


def load_tweeted(db):
    """ツイート済みエントリーの日時を取得"""
    return db.get(REDIS_KEY_TWEETED)


def save_tweeted(db, updated):
    """ツイート済みエントリーの日時を保存"""
    db.set(REDIS_KEY_TWEETED, updated)


def filter_untweeted(entries, tweeted):
    """未ツイートのエントリーを取得"""
    return filter(lambda entry: entry.updated > tweeted, entries)


def convert_utc_struct_time_to_localtime(utc_struct_time):
    """UTCのtime.struct_timeをlocaltimeへ変換"""
    epoch = calendar.timegm(utc_struct_time)
    return time.localtime(epoch)


def main():
    """メイン"""
    # Redisへ接続
    db = redis.from_url(
        REDIS_URL,
        charset='utf-8',
        decode_responses=True
    )

    # RSSフィードの取得
    d = feedparser.parse(FEED_URL)
    if d.status >= 400:
        print('エラー: ステータスコードが400以上')
        print(d.status)
        sys.exit(1)

    # ツイート済みエントリーの日時を取得
    tweeted = load_tweeted(db)
    if tweeted is None:
        if len(d.entries) > UNTWEETED_MAX_NUM:
            tweeted = d.entries[UNTWEETED_MAX_NUM].updated
        else:
            tweeted = ''

    # Twitterで認証する
    try:
        api = twitter_authentication(
            TWITTER_API_KEY,
            TWITTER_API_SECRET_KEY,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET
        )
    except tweepy.TweepError as e:
        print('エラー: Twitterの認証に失敗')
        print(e)
        sys.exit(1)

    # エントリーをTwitterへ投稿
    for entry in filter_untweeted(reversed(d.entries), tweeted):
        # UTCになっているupdated_parsedを日本時間へ変換
        updated = convert_utc_struct_time_to_localtime(entry.updated_parsed)
        datetime_str = time.strftime('%m/%d %H:%M', updated)

        # 投稿する文章を作成
        status = datetime_str + ' ' + entry.title
        print(status)

        # Twitterへ投稿
        try:
            api.update_status(
                status[:MAX_TWEET_CHAR]
                + ' '
                + entry.link
            )
            time.sleep(5)
        except tweepy.TweepError as e:
            print('エラー: Twitterへの投稿に失敗')
            print(e)
            sys.exit(1)

    # ツイート済みエントリーの日時を保存
    save_tweeted(db, d.entries[0].updated)


if __name__ == '__main__':
    main()
