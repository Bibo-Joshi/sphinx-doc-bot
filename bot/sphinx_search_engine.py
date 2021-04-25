#!/usr/bin/env python3
"""The module contains the classes :class:`SphinxSearchEngine` and :class:`SphinxDocEntry`."""
import heapq
import itertools
import re
from functools import lru_cache
from threading import Lock
import datetime as dtm
from typing import Optional, Dict, List, Tuple
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from rapidfuzz import fuzz
from sphinx.util.inventory import InventoryFile
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import MAX_INLINE_QUERY_RESULTS

PreProcessedQuery = List[str]


class SphinxDocEntry:  # pylint: disable=R0903
    """This class represents an entry in a Sphinx documentation.

    Args:
        project_name: Name of the project this entry belongs to.
        version: Version of the project.
        url: URL to the online documentation of the entry.
        entry_type: Which type of entry this is.
        name: Name of the entry.
        display_name: Optional. Display name for the entry.

    Attributes:
        project_name (:obj:`str`): Name of the project this entry belongs to.
        version (:obj:`str`): Version of the project.
        url (:obj:`str`): URL to the online documentation of the entry.
        entry_type (:obj:`str`): Which type of entry this is.
        name (:obj:`str`): Name of the entry.
        display_name (:obj:`str`): Optional. Display name for the entry.

    """

    def __init__(  # pylint: disable=R0913
        self,
        project_name: str,
        version: str,
        url: str,
        entry_type: str,
        name: str,
        display_name: str = None,
    ) -> None:
        self.project_name = project_name
        self.version = version
        self.url = url
        self.entry_type = entry_type
        self.name = name
        self.display_name = display_name
        self._parsed_name: Optional[PreProcessedQuery] = None

    def compare_to(self, query: str, processed_query: PreProcessedQuery) -> float:
        """
        Compares this entry to a query.

        Args:
            query: The query as plain string.
            processed_query: The Query, preprocessed by :meth:`SphinxSearchEngine.parse_query`

        Returns:
            The comparison score.
        """
        if self._parsed_name is None:
            self._parsed_name = SphinxSearchEngine.parse_query(self.name)
        score = 0.0

        # We compare all the single parts of the query …
        for target, value in zip(processed_query, self._parsed_name):
            score += fuzz.ratio(target, value)
        # … and the full name because we're generous
        score += fuzz.ratio(query, self.name)

        # IISC std: is the domain for general stuff like headlines and chapters.
        # we'll wanna give those a little less weight
        if self.entry_type.startswith('std:'):
            score *= 0.8
        return score


class SphinxSearchEngine:
    """Class to handle fetching and searching Sphinx documentation.

    Args:
        url: URL of the Sphinx documentation.
        cache_timeout: Cache timeout in minutes. Documentation will be fetched at most every
            ``cache_timeout`` minutes.

    Attributes:
        url (:obj:`str`): URL of the Sphinx documentation.
        cache_timeout (:obj:`datetime.timedelta`): Cache timeout as :obj:`datetime.timedelta`.
    """

    def __init__(self, url: str, cache_timeout: int) -> None:
        self.url = url
        self.cache_timeout = dtm.timedelta(minutes=cache_timeout)
        self._last_cache_time: Optional[dtm.datetime] = None
        self._user_agent = 'GitLab: HirschHeissIch/sphinx-doc-bot'
        self._request = Request(
            urljoin(self.url, 'objects.inv'), headers={'User-Agent': self._user_agent}
        )
        self._doc_data: Dict[str, SphinxDocEntry] = {}
        self.__lock = Lock()

        # fetch docs for the first time
        self.fetch_docs()

    @property
    def project_description(self) -> str:
        """The description of this project as reported by the fetched documentation"""
        return next(entry for entry in self._doc_data.values()).project_name

    @staticmethod
    def parse_query(query: str) -> PreProcessedQuery:
        """
        Does some preprocessing of the query needed for comparison with the entries in the docs.

        Args:
            query: The search query.

        Returns:
            The query, split on ``.``, ``-`` and ``/``, in reversed order.
        """
        # reversed, so that 'class' matches the 'class' part of 'module.class' exactly instead of
        # not matching the 'module' part
        return list(reversed(re.split(r'\.|/|-', query.strip())))

    def fetch_docs(self, cached: bool = True) -> None:
        """
        Fetches the documentation.

        Args:
            cached: Whether to respect caching or not. Defaults to :obj:`True`.
        """
        now = dtm.datetime.now()

        if (
            cached
            and self._last_cache_time is not None
            and self._last_cache_time + self.cache_timeout <= now
        ):
            return

        self._last_cache_time = now
        docs_data = urlopen(self._request)
        with self.__lock:
            data = InventoryFile.load(docs_data, self.url, urljoin)
            for entry_type, items in data.items():
                for name, (project_name, version, url, display_name) in items.items():
                    self._doc_data[name] = SphinxDocEntry(
                        name=name,
                        project_name=project_name,
                        version=version,
                        url=url,
                        display_name=display_name if display_name.strip() != '-' else None,
                        entry_type=entry_type,
                    )
            # This is important: If the docs have changed the cache is useless
            self.search.cache_clear()

    @lru_cache(maxsize=256)
    def search(self, query: str, count: int = None) -> List[SphinxDocEntry]:
        """Compares the query to all entries in the documentation and returns them in the order
        of similarity.

        Args:
            query: The search query
            count: Optional. If passed, returns the ``count`` elements with highest comparison
                score.

        Returns:
            The sorted results.
        """
        processed_query = self.parse_query(query)
        with self.__lock:
            entries = list(self._doc_data.values())

            def sort_key(entry: SphinxDocEntry) -> float:
                return entry.compare_to(query, processed_query)

            if not count:
                return sorted(
                    entries,
                    key=sort_key,
                    # We want high values first
                    reverse=True,
                )
            return heapq.nlargest(count, entries, key=sort_key)

    @lru_cache(maxsize=256)
    def inline_search_results(self, query: str, page: int = 0) -> List[InlineQueryResultArticle]:
        """Builds inline results from the results of :meth:`search`.

        Args:
            query: The search query.
            page: The pagination index.

        Returns:
            The inline results.

        """
        sorted_entries = self.search(query)[
            page * MAX_INLINE_QUERY_RESULTS : (page + 1) * MAX_INLINE_QUERY_RESULTS  # noqa: E203
        ]
        return [
            InlineQueryResultArticle(
                id=str(i + page * MAX_INLINE_QUERY_RESULTS),
                title=entry.name,
                input_message_content=InputTextMessageContent(
                    f'Documentation of <i>{entry.project_name}</i>: <a href="{entry.url}">'
                    f'{entry.display_name or entry.name}</a>'
                ),
                description=(
                    f'Documentation of {entry.project_name}'
                    f'{", " + entry.display_name if entry.display_name else ""}'
                ),
            )
            for i, entry in enumerate(sorted_entries)
        ]

    @lru_cache(256)
    def multi_search_combinations(
        self, queries: Tuple[str], results_per_query: int = 3
    ) -> List[Dict[str, SphinxDocEntry]]:
        """For each query, runs :meth:`search` and fetches the ``results_per_query`` most likely
        results. Then builds all possible combinations.

        Args:
            queries: The search queries.
            results_per_query: Optional. Number of results to fetch per query. Defaults to ``3``.

        Returns:
            All possible result combinations. Each list entry is a dictionary mapping each query
                to the corresponding :class:`SphinxDocEntry`.

        """
        # Don't use a page-argument here, as the number of results will usually be relatively small
        # so we can just build the list once and get slices from the cached result if necessary

        results = {query: self.search(query=query, count=results_per_query) for query in queries}

        return [
            dict(zip(queries, query_results))
            for query_results in itertools.product(*results.values())
        ]
