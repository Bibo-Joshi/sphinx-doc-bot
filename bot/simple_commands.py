#!/usr/bin/env python3
"""The module contains some basic functionality."""
from typing import cast

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes

from bot.constants import SSE_KEY, USER_GUIDE
from bot.sphinx_search_engine import SphinxSearchEngine


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Returns some info about the bot.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    sse = cast(SphinxSearchEngine, context.bot_data[SSE_KEY])
    text = (
        f"Hi! I am <b>{context.bot.bot.full_name}</b> and here to help you search "
        f"the Documentation of <i>{sse.project_description}</i>."
        "\n\nFor details on how to use me, please visit the user guide below. 🙂."
    )

    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton("User Guide 🤖", url=USER_GUIDE),
            InlineKeyboardButton(f"Documentation of {sse.project_description}", url=sse.url),
        ]
    )

    await cast(Message, update.effective_message).reply_text(text, reply_markup=keyboard)
