#!/usr/bin/env python3
"""The module contains functions that register the handlers."""
from telegram.ext import Application, CommandHandler, InlineQueryHandler

from bot.constants import ADMIN_KEY, ENCLOSED_REGEX, SSE_KEY
from bot.error_handler import error_handler
from bot.inline import direct_search, insert_search
from bot.simple_commands import info
from bot.sphinx_search_engine import SphinxSearchEngine


async def setup_application(
    application: Application, cache_timeout: int, admin: int, docs_url: str
) -> None:
    """
    Registers the different handlers, prepares ``chat/user/bot_data`` etc.

    Args:
        application: The application.
        cache_timeout: Timeout for YOURLS statistics cache.
        admin: The admins Telegram chat ID.
        docs_url: The URL of the Sphinx docs.

    """
    application.bot_data[ADMIN_KEY] = admin
    sse = SphinxSearchEngine(url=docs_url, cache_timeout=cache_timeout)
    application.bot_data[SSE_KEY] = sse
    await sse.initialize(application=application)

    application.add_handler(CommandHandler(["start", "help", "info"], info))
    application.add_handler(InlineQueryHandler(insert_search, pattern=ENCLOSED_REGEX))

    application.add_handler(InlineQueryHandler(direct_search))

    await application.bot.set_my_commands(
        [
            ("help", "Display general information"),
        ]
    )

    application.add_error_handler(error_handler)
