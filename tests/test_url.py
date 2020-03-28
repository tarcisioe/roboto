"""Tests for roboto.url."""
import pytest

from roboto.url import URL, InvalidURL


def test_valid_url_is_ok() -> None:
    """Ensure that `URL.make` accepts a valid URL."""
    URL.make('https://google.com')


def test_invalid_url_raises() -> None:
    """Ensure that `URL.make` raises with an invalid URL."""
    with pytest.raises(InvalidURL):
        URL.make('not valid')
