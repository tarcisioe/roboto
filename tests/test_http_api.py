"""Tests for the `http_api` module."""
from typing import Any

import pytest

from roboto.error import BotAPIError
from roboto.http_api import AnyAPIResponse, validate_response


def test_validate_good_response() -> None:
    """Ensure validate_response returns result if ok is True."""
    response: Any = AnyAPIResponse(ok=True, result=[])

    assert validate_response(response) == []


def test_validate_bad_response() -> None:
    """Ensure validate_response raises if ok is False."""
    response: Any = AnyAPIResponse(
        ok=False, error_code=400, description='There was error.'
    )

    try:
        validate_response(response)
    except BotAPIError as e:
        assert e.error_code == 400
        assert e.description == 'There was error.'
    else:
        pytest.fail('No exception thrown.')
