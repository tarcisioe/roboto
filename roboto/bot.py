"""The main bot class for Roboto."""
from dataclasses import InitVar, dataclass, field
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientSession

from .datautil import from_json
from .error import BotAPIError
from .types import APIResponse, Token, User
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

    async def make_request(self, method: str, endpoint: str, body: Any = None) -> Any:
        """Basic request function for the telegram API"""
        url = urljoin(self.api_url, endpoint)

        if body is not None:
            body = {k: v for k, v in body._asdict().items() if v is not None}

        async with ClientSession() as s:
            content = await s.request(method, url, json=body)

        response: APIResponse = from_json(APIResponse, await content.json())

        if not response.ok:
            raise BotAPIError('Faled to read response from Telegram Bot API')

        return response.result

    async def get_me(self) -> User:
        """getMe API method.

        Returns:
            User: the user object representing the bot itself.
        """
        return from_json(User, await self.make_request('GET', 'getMe'))


__all__ = [
    'BotAPI',
]
