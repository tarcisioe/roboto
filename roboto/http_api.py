"""Bot API request function."""
from enum import Enum
from typing import Any

from asks import Session

from .datautil import from_json, to_json
from .error import BotAPIError
from .types import APIResponse


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
    session: Session, method: HTTPMethod, api_method: str, body: Any = None
) -> Any:
    """Basic request function for the telegram API

    Args:
        session: An `asks.Session` object with the correct `base_location` and
                 `endpoint` set up.
        method: The HTTP method to use.
        body: An object to send as JSON.

    Returns:
        The APIResponse contents if everything went right.

    Raises:
        BotAPIError: If response.ok is false.
    """
    if body is not None:
        body = to_json(body)

    content = await session.request(method.value, path=api_method, json=body)

    response = from_json(APIResponse, content.json())

    return validate_response(response)
