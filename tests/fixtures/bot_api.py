"""Fixture for mocking the HTTP session of a BotAPI."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator, Tuple

import pytest

from roboto import BotAPI, Token

from ..common import AsyncMock, MagicMock, MockedBotAPI
from .async_mocker import AsyncMockFixture


@pytest.fixture
def request_response(
    async_mocker: AsyncMockFixture,
) -> Generator[Tuple[AsyncMock, MagicMock], None, None]:
    """Mock the request method of a Session.

    Returns:
        The mocked request method and the mock returned as its response.
    """
    response = MagicMock()
    response.json = MagicMock()
    request = AsyncMock(return_value=response)

    @asynccontextmanager
    async def make_mock_session(*_, **_2):
        mock_session = async_mocker.MagicMock()
        mock_session.request = request
        yield mock_session

    async_mocker.patch('roboto.bot.Session', make_mock_session)

    yield request, response


@pytest.fixture
async def mocked_bot_api(
    request_response,  # pylint: disable=redefined-outer-name
) -> AsyncGenerator[MockedBotAPI, None]:
    """Fixture for creating a BotAPI with a fake http session for testing."""

    request, response = request_response

    async with BotAPI.make(Token('dummy')) as api:
        yield MockedBotAPI(request, response, api)
