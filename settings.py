from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # RSSフィードのURL
    feed_url: str
    # Twitter Consumer Key
    consumer_key: str
    # Twitter Consumer Secret
    consumer_secret: str
    # Twitter Access Token
    access_token: str
    # Twitter Access Token Secret
    access_token_secret: str
    # Misskeyのインスタンスアドレス
    misskey_address: str | None
    # MisskeyのAPIトークン
    misskey_token: str | None

    # ツイート済み日時が保存されていない場合にツイートする最大数
    untweeted_max_num: int = 3
    # 連続でツイートを送信する場合の間隔(秒)
    tweet_interval: int = 5

    # ツイート済み日時を書き込むファイル名
    tweeted_file: str = 'tweeted'
    # URLを除いたツイートの最大文字数
    max_tweet_char: int = 128
    # ログ出力の設定ファイル
    logging_config_file: str = 'logging_config.json'


settings = Settings()
