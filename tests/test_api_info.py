"""Tests for roboto.api_info."""

from roboto.api_info import Token, api_url
from roboto.url import URL


def test_api_info_makes_a_valid_url() -> None:
    """Ensure api_url returns a valid URL."""
    url = api_url(Token('dummytoken123'))

    assert isinstance(url, URL)
