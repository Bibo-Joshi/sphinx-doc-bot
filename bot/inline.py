#!/usr/bin/env python3
"""The module contains functions for the inline mode."""
import re
from typing import cast, Tuple

from telegram import Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackContext

from bot.constants import SSE_KEY, ENCLOSED_REGEX, ENCLOSING_CHAR
from bot.sphinx_search_engine import SphinxSearchEngine


def direct_search(update: Update, context: CallbackContext) -> None:
    """
    Puts the inline query directly through :meth:`SphinxSearchEngine.inline_results` and displays
    the corresponding results.

    Args:
        update: The incoming Telegram update containing a message.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    inline_query = cast(InlineQuery, update.inline_query)
    if not inline_query.query:
        return
    sse = cast(SphinxSearchEngine, context.bot_data[SSE_KEY])
    inline_query.answer(
        results=lambda page: sse.inline_search_results(inline_query.query, page=page),
        auto_pagination=True,
    )


def insert_search(update: Update, context: CallbackContext) -> None:
    """
    Searches for results for all terms enclosed in ``+`` and displays corresponding results.

    Args:
        update: The incoming Telegram update containing a message.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    inline_query = cast(InlineQuery, update.inline_query)
    if not inline_query.query:
        return
    sse = cast(SphinxSearchEngine, context.bot_data[SSE_KEY])

    queries = cast(Tuple[str], tuple(re.findall(ENCLOSED_REGEX, inline_query.query)))
    combinations = sse.multi_search_combinations(queries)

    inline_results = []
    for i, combination in enumerate(combinations):
        text = inline_query.query
        for query, entry in combination.items():
            text = text.replace(
                f'{ENCLOSING_CHAR}{query}{ENCLOSING_CHAR}',
                f'<a href="{entry.url}">{entry.name}</a>',
            )
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),
                title=f'Insert links to the documentation of {sse.project_description}',
                input_message_content=InputTextMessageContent(text),
                description=', '.join(entry.name for entry in combination.values()),
            )
        )

    inline_query.answer(results=inline_results, auto_pagination=True)
