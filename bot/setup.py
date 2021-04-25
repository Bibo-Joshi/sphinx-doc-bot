#!/usr/bin/env python3
"""The module contains functions that register the handlers."""
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    InlineQueryHandler,
)

from bot.constants import ADMIN_KEY, SSE_KEY, ENCLOSED_REGEX
from bot.error_handler import error_handler
from bot.inline import direct_search, insert_search
from bot.simple_commands import info
from bot.sphinx_search_engine import SphinxSearchEngine


def setup_dispatcher(
    dispatcher: Dispatcher, cache_timeout: int, admin: int, docs_url: str
) -> None:
    """
    Registers the different handlers, prepares ``chat/user/bot_data`` etc.

    Args:
        dispatcher: The dispatcher.
        cache_timeout: Timeout for YOURLS statistics cache.
        admin: The admins Telegram chat ID.
        docs_url: The URL of the Sphinx docs.

    """
    dispatcher.bot_data[ADMIN_KEY] = admin
    dispatcher.bot_data[SSE_KEY] = SphinxSearchEngine(url=docs_url, cache_timeout=cache_timeout)

    dispatcher.add_handler(CommandHandler(['start', 'help', 'info'], info))
    dispatcher.add_handler(InlineQueryHandler(insert_search, pattern=ENCLOSED_REGEX))

    dispatcher.add_handler(InlineQueryHandler(direct_search))

    dispatcher.bot.set_my_commands(
        [
            ('help', 'Display general information'),
        ]
    )

    dispatcher.add_error_handler(error_handler)
