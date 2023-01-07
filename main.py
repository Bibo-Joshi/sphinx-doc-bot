#!/usr/bin/env python3
"""The script that runs the bot."""
import functools
import logging
from configparser import ConfigParser

from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Defaults

from bot.setup import setup_application

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="sphinx-doc-bot.log",
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    # Read configuration values from bot.ini
    config = ConfigParser()
    config.read("bot.ini")
    token = config["sphinx-doc-bot"]["token"]
    cache_timeout = int(config["sphinx-doc-bot"]["cache_timeout"])
    admin = int(config["sphinx-doc-bot"]["admins_chat_id"])
    docs_url = config["sphinx-doc-bot"]["docs_url"]

    # Create the Updater and pass it your bot's token.
    defaults = Defaults(
        parse_mode=ParseMode.HTML, disable_notification=True, disable_web_page_preview=True
    )
    application = (
        ApplicationBuilder()
        .token(token)
        .defaults(defaults)
        .post_init(
            functools.partial(
                setup_application, cache_timeout=cache_timeout, admin=admin, docs_url=docs_url
            )
        )
        .build()
    )
    application.run_polling()


if __name__ == "__main__":
    main()
