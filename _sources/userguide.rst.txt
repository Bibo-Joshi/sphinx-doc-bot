Non-Functionality
=================

Via the `/help` command, a simple information message is shown. It will include the link to both this page and the
documentation that the bot instance is configured for.

Direct Search
=============

To search for an entry in the documentation, the inline mode is used. In any Telegram chat, type ``@your_bot query`` and
the bot will display a list of results sorted by similarity between the query and the result. Select one of the results
to send a message that will include a link to this documentation entry.

.. note::
    Sorting by »best match« is often not as easy as it sounds. You might have to scroll a bit.

Insert Search
=============

You can also directly include links into a text message. This is done by again using the bots inline mode and enclosing
any search query with a ``+`` character, e.g. ``@your_bot foo +query_1+ bar +query_2+``. For each search query, the
three best matching results will be fetched and the results will list all possible combinations of those. Select one of
the results to send a message with the links inserted into your text.

.. note::
    Telegram only parses inline queries up to 256 characters. Anything above that will be cut off.
