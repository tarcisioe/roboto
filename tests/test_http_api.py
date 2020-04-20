"""Tests for the `http_api` module."""
import pytest

from roboto.error import BotAPIError
from roboto.http_api import APIResponse, validate_response


def test_validate_response() -> None:
    """Ensure validate response validates responses."""
    assert validate_response(APIResponse(ok=True, result=[])) == []

    try:
        validate_response(
            APIResponse(ok=False, error_code=400, description='There was error.')
        )
    except BotAPIError as e:
        assert e.error_code == 400
        assert e.description == 'There was error.'
    else:
        pytest.fail('No exception thrown.')
