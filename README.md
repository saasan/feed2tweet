# feed2tweet

RSSフィードを X (旧 Twitter) / Misskey へ投稿する

## 事前準備

### X (旧 Twitter)

API 有料化後も自分のアカウントだけなら無料でポスト(ツイート)できるので、
ポストしたいアカウントで以下を行う。

1. X のポストしたいアカウントで開発者として登録
2. Developer Portal でプロジェクトとアプリを設定
3. アプリの User authentication settings を編集し App permissions を Read and write へ変更
4. API の Consumer Keys, Access Token and Secret を取得

### Misskey

ノートを作成したいアカウントで以下を行う。

1. 設定 > API アクセストークンの発行
2. 名前を入力し、権限「ノートを作成・削除する」をつけて発行
3. 確認コード (API トークン) を取得

## ローカルで実行する場合の設定

以下の環境変数を設定するか .env ファイルに書く。

    # RSSフィードのURL
    FEED_URL='https://example.com/rss.xml'
    # Twitter Consumer Key
    CONSUMER_KEY='*****'
    # Twitter Consumer Secret
    CONSUMER_SECRET='*****'
    # Twitter Access Token
    ACCESS_TOKEN='*****'
    # Twitter Access Token Secret
    ACCESS_TOKEN_SECRET='*****'
    # Misskeyのインスタンスアドレス (Misskeyへ投稿しない場合は不要)
    MISSKEY_ADDRESS=example.com
    # MisskeyのAPIトークン (Misskeyへ投稿しない場合は不要)
    MISSKEY_TOKEN='*****'
    # ツイート済み日時が保存されていない場合にツイートする最大数 (任意)
    UNTWEETED_MAX_NUM=3
    # 連続でツイートを送信する場合の間隔(秒) (任意)
    TWEET_INTERVAL=5

## GitHub Actions での設定

リポジトリの Settings > Secrets and variables > Actions
で Variables と Secrets を設定する。

- Variables
  - FEED_URL
  - MISSKEY_ADDRESS
  - UNTWEETED_MAX_NUM
  - TWEET_INTERVAL
- Secrets
  - CONSUMER_KEY
  - CONSUMER_SECRET
  - ACCESS_TOKEN
  - ACCESS_TOKEN_SECRET
  - MISSKEY_TOKEN

## GitHub Actions での実行

.github/workflows/feed2tweet.yml で10分に1回実行する設定としている。

## GitHub Actions でのキャッシュ

actions/setup-python@v4 で構築した環境と、
最後に実行した UNIX 時間を保持する tweeted
という名前のファイルをキャッシュとして保持する。
古いキャッシュは自動で削除されるため特に問題ないが、
気になる場合はリポジトリの Actions > Caches から削除できる。

## 未ツイートのエントリーを抽出する方法について

未ツイートのエントリーは、RSS の updated
と最後に実行した UNIX 時間を保持する tweeted を比較することで抽出している。
これは作者がツイートさせたい RSS に合わせた仕様のため、
ツイートさせる RSS の内容によっては
feed2tweet.py 内の filter_untweeted 関数を変更する必要がある。
