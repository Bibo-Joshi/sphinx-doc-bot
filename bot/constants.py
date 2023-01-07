#!/usr/bin/env python
"""This module contains constants used throughout the bot."""
import re
from urllib.parse import urljoin

HOMEPAGE: str = "https://Bibo-Joshi.github.io/sphinx-doc-bot/"
""":obj:`str`: Homepage of this bot."""
USER_GUIDE: str = urljoin(HOMEPAGE, "userguide.html")
""":obj:`str`: User guide for this bot."""

ENCLOSING_CHAR = "+"
""":obj:`str`: Character that marks the beginning & end of a search query in an inline search."""
ENCLOSED_REGEX = re.compile(
    rf"[^{ENCLOSING_CHAR}]*\{ENCLOSING_CHAR}([a-zA-Z_/.0-9]*)\{ENCLOSING_CHAR}"
)
""":obj:`re.Pattern`: Pattern that matches any search query enclosed in :attr:`ENCLOSING_CHAR`."""

SSE_KEY = "search_key"
""":obj:`str`: The key of ``bot_data`` where the :class:`bot.search.SphinxSearchEngine` is stored.
"""
ADMIN_KEY = "admin_key"
""":obj:`str`: The key of ``bot_data`` where the admins chat id is stored."""
