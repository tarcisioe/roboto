"""Common utilities for tests."""
import sys
from dataclasses import dataclass
from unittest.mock import MagicMock

from roboto.bot import BotAPI

if sys.version_info < (3, 8):
    from asynctest.mock import (  # pylint: disable=import-error
        CoroutineMock as AsyncMock,
    )
else:
    from unittest.mock import AsyncMock  # pylint: disable=import-error


@dataclass
class MockedBotAPI:
    """Aggregate for a mocked request/response pair and a bot API."""

    request: AsyncMock
    response: MagicMock
    api: BotAPI
