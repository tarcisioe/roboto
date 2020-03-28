"""Information to access the Telegram Bot API."""
from dataclasses import dataclass

from .url import URL


class Token(str):
    """Strong type for API tokens."""


@dataclass(frozen=True)
class APIInfo:
    """Type representing a Bot."""

    token: Token
    url: URL


def api_url(token: Token) -> URL:
    """Get the API url based on the bot token."""
    return URL.make(f'https://api.telegram.org/bot{token}/')
