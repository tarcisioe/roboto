"""Bot API request function."""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Optional, Union

from typing_extensions import Literal, Protocol

from .api_types import FileDescription
from .asks import Session
from .asks.multipart import BytesMultipartData, IOMultipartData
from .asks.response_objects import Response
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


async def _json_request(
    session: Session, method: HTTPMethod, api_method: str, body: Any = None
) -> Response:
    return await session.request(method.value, path=api_method, json=to_json(body))


def _to_multipart_compatible(value: Any) -> Any:
    """Transform values into multipart/form-data compatible versions."""
    if isinstance(value, FileDescription):
        if isinstance(value.binary_source, bytes):
            return BytesMultipartData(
                value.binary_source, value.mime_type, value.basename
            )

        return IOMultipartData(value.binary_source, value.mime_type, value.basename)

    return value


async def _multipart_request(
    session: Session, method: HTTPMethod, api_method: str, body: Any = None
) -> Response:
    fields = {
        k: _to_multipart_compatible(v)
        for k, v in body.__dict__.items()
        if v is not None
    }

    return await session.request(method.value, path=api_method, multipart=fields)


APIRequester = Callable[[Session, HTTPMethod, str, Any], Awaitable[Response]]


async def _make_request(
    requester: APIRequester,
    session: Session,
    method: HTTPMethod,
    api_method: str,
    body: Any = None,
) -> Any:
    content = await requester(session, method, api_method, body)

    # We know that the server ensures the object will follow either protocol,
    # but mypy can't see that.
    response: Any = from_json(AnyAPIResponse, content.json())

    return validate_response(response)


async def make_request(
    session: Session, method: HTTPMethod, api_method: str, body: Any = None
) -> Any:
    """Basic request function for the telegram API

    Args:
        session: An `asks.Session` object with the correct `base_location` and
                 `endpoint` set up.
        method: The HTTP method to use.
        api_method: The Telegram API method to call.
        body: An object to send as JSON.

    Returns:
        The APIResponse contents if everything went right.

    Raises:
        BotAPIError: If response.ok is false.
    """
    return await _make_request(_json_request, session, method, api_method, body)


async def make_multipart_request(session: Session, api_method: str, body: Any) -> Any:
    """Function for doing POST multipart/form-data requests.

    Useful for requests that send files.

    Args:
        session: An `asks.Session` object with the correct `base_location` and
                 `endpoint` set up.
        api_method: The HTTP method to use.
        body: An object to send as JSON.

    Returns:
        The APIResponse contents if everything went right.

    Raises:
        BotAPIError: If response.ok is false.
    """
    return await _make_request(
        _multipart_request, session, HTTPMethod.POST, api_method, body
    )
