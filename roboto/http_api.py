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


def validate_response(response: APIResponse) -> Any:
    """Validate a Telegram Bot API Response.

    Args:
        response: A Telegram Bot API response to validate.

    Returns:
        The contents of the response if it response.ok is true.

    Raises:
        BotAPIError: If response.ok is false.
    """
    if response.result is None:
        assert response.error_code is not None and response.description is not None
        raise BotAPIError(
            response.error_code, response.description,
        )

    assert response is not None
    return response.result


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

    response = from_json(APIResponse, await content.json())

    return validate_response(response)
