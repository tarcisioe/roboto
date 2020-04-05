"""Bot API request function."""
from enum import Enum
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientSession

from .datautil import from_json, to_json
from .error import BotAPIError
from .types import APIResponse
from .url import URL


class HTTPMethod(Enum):
    """HTTP Methods"""

    GET = 'get'
    POST = 'post'
    PUT = 'put'


async def make_request(
    api_url: URL, method: HTTPMethod, endpoint: str, body: Any = None
) -> Any:
    """Basic request function for the telegram API

    Args:
        api_url: The bot API URL (including token).
        method:

    Returns:
        The APIResponse contents if everything went right.

    Raises:
        BotAPIError: If response.ok is false.
    """
    url = urljoin(api_url, endpoint)

    if body is not None:
        body = to_json(body)

    async with ClientSession() as s:
        content = await s.request(method.value, url, json=body)

    response: APIResponse = from_json(APIResponse, await content.json())

    if response.result is None:
        assert response.error_code is not None and response.description is not None
        raise BotAPIError(
            response.error_code, response.description,
        )

    return response.result
