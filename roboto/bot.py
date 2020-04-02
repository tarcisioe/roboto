"""The main bot class for Roboto."""
from dataclasses import InitVar, dataclass, field

from .datautil import from_json
from .http import HTTPMethod, make_request
from .types import BotUser, Token
from .url import URL


@dataclass
class BotAPI:
    """Bot API wrapper."""

    token: InitVar[Token]
    api_url: URL = field(init=False)

    def __post_init__(self, token: Token) -> None:
        """Constructor for bot objects.

        Args:
            token: The Bot API token.
        """
        self.api_url = URL.make(f'https://api.telegram.org/bot{token}/')

    async def get_me(self) -> BotUser:
        """getMe API method.

        Returns:
            User: the user object representing the bot itself.
        """
        return from_json(
            BotUser, await make_request(self.api_url, HTTPMethod.GET, 'getMe')
        )


__all__ = [
    'BotAPI',
]
