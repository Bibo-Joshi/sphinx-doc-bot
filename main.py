#!/usr/bin/env python3
"""The script that runs the bot."""
import logging
from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, Defaults

from bot.setup import setup_dispatcher

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='sphinx-doc-bot.log',
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    # Read configuration values from bot.ini
    config = ConfigParser()
    config.read('bot.ini')
    token = config['sphinx-doc-bot']['token']
    cache_timeout = int(config['sphinx-doc-bot']['cache_timeout'])
    admin = int(config['sphinx-doc-bot']['admins_chat_id'])
    docs_url = config['sphinx-doc-bot']['docs_url']

    # Create the Updater and pass it your bot's token.
    defaults = Defaults(
        parse_mode=ParseMode.HTML, disable_notification=True, disable_web_page_preview=True
    )
    updater = Updater(token, defaults=defaults)

    # Register handlers
    setup_dispatcher(updater.dispatcher, cache_timeout, admin, docs_url=docs_url)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
