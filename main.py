import json
import logging
import logging.config
from feed2tweet import Feed2Tweet
from settings import settings


def setup_logger(name: str) -> logging.Logger:
    """ログ出力の設定"""
    with open(settings.logging_config_file, encoding='utf-8') as f:
        logging_config = json.load(f)
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(name)

    return logger


def main() -> None:
    setup_logger(__name__)
    feed2tweet = Feed2Tweet()
    feed2tweet.fetch_and_post_rss()


if __name__ == '__main__':
    main()
