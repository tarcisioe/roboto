"""Strongly-typed URLs."""
from __future__ import annotations

import validators


class InvalidURL(Exception):
    """Signal that a given URL is invalid."""


class URL(str):
    """Strong type for URLs.

    Should not be instantiated directly. Use the `make` staticmethod.
    """

    @staticmethod
    def make(url: str) -> URL:
        """Check a string for validity and return a URL checked string.

        Args:
            url: A candidate string.

        Returns:
            The same string as a `URL` instance.

        Raises:
            InvalidURL: If the string is not a valid URL.
        """
        result = validators.url(url)

        if not result:
            raise InvalidURL(f'"{url}" is not a valid URL.')

        return URL(url)
