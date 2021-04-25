#!/usr/bin/env python3
"""The module contains the error handler."""
import html
import json
import logging
import traceback
from typing import cast

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from bot.constants import ADMIN_KEY

logger = logging.getLogger(__name__)


def error_handler(update: object, context: CallbackContext) -> None:
    """
    Log the error and send a Telegram message to notify the admin.

    Args:
        update: The incoming update. Not necessarily a Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, cast(Exception, context.error).__traceback__
    )
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message_1 = (
        f'An exception was raised while handling an update\n\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>'
    )
    message_2 = f'<pre>{html.escape(tb_string)}</pre>'

    # Finally, send the messages
    # We send update and traceback in two parts to reduce the chance of hitting max length
    admin_id = context.bot_data[ADMIN_KEY]
    try:
        sent_message = context.bot.send_message(chat_id=admin_id, text=message_1)
        sent_message.reply_html(message_2)
    except BadRequest as exc:
        if 'too long' in str(exc):
            message = (
                f'Hey.\nThe error <code>{html.escape(str(context.error))}</code> happened.'
                f' The traceback is too long to send, but it was written to the log.'
            )
            context.bot.send_message(chat_id=admin_id, text=message)
        else:
            raise exc
