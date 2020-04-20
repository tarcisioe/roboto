"""Bot API request function."""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

from asks import Session
from typing_extensions import Literal, Protocol

from .datautil import from_json, to_json
from .error import BotAPIError


class APIResult(Protocol):
    """API success response."""

    ok: Literal[True]
    result: Any = None


class APIError(Protocol):
    """API error response."""

    ok: Literal[False]
    error_code: int
    description: str


APIResponse = Union[APIResult, APIError]


@dataclass(frozen=True)
class AnyAPIResponse:
    """API Response format."""

    ok: bool
    result: Optional[Any] = None
    error_code: Optional[int] = None
    description: Optional[str] = None


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
    if not response.ok:
        raise BotAPIError(
            response.error_code, response.description,
        )

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

    # We know that the server ensures the object will follow either protocol,
    # but mypy can't see that.
    response: Any = from_json(AnyAPIResponse, content.json())

    return validate_response(response)
