"""Common utilities for tests."""
from dataclasses import dataclass

from asynctest.mock import CoroutineMock as AsyncMock
from asynctest.mock import MagicMock

from roboto.bot import BotAPI


@dataclass
class MockedBotAPI:
    """Aggregate for a mocked request/response pair and a bot API."""

    request: AsyncMock
    response: MagicMock
    api: BotAPI
