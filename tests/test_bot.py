"""Tests for the roboto.bot module."""
from typing import Tuple
from unittest.mock import MagicMock

import pytest

from roboto import (
    BotUser,
    Chat,
    ChatID,
    Message,
    MessageID,
    Token,
    Update,
    User,
    UserID,
)
from roboto.bot import BotAPI

from .common import MockedBotAPI


@pytest.mark.trio
async def test_bot_api_make(request_response: Tuple[MagicMock, MagicMock]):
    """Test BotAPI creation makes no requests."""
    request, _ = request_response

    async with BotAPI.make(Token('dummy')) as _:
        pass

    request.assert_not_awaited()


@pytest.mark.trio
async def test_get_me(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.get_me produces a BotUser given the correct input."""
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'id': 1,
            'is_bot': True,
            'first_name': 'Mock',
            'can_join_groups': True,
            'can_read_all_group_messages': True,
            'supports_inline_queries': False,
        },
    }

    bot_user = await mocked_bot_api.api.get_me()

    mocked_bot_api.request.assert_called_once()

    assert bot_user == BotUser(
        id=UserID(1),
        is_bot=True,
        first_name='Mock',
        can_join_groups=True,
        can_read_all_group_messages=True,
        supports_inline_queries=False,
    )


@pytest.mark.trio
async def test_get_updates_empty(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.get_updates produces an empty list when there are no updates."""
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': [],
    }

    updates = await mocked_bot_api.api.get_updates(0)

    mocked_bot_api.request.assert_called_once()

    assert updates == []


@pytest.mark.trio
async def test_get_updates(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.get_updates properly reads updates."""
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': [
            {
                'update_id': 1,
                'message': {
                    'message_id': 1,
                    'date': 0,
                    'chat': {'id': 1, 'type': 'private'},
                    'from': {'id': 1, 'is_bot': False, 'first_name': 'Test'},
                },
            }
        ],
    }

    updates = await mocked_bot_api.api.get_updates(0)

    mocked_bot_api.request.assert_called_once()

    assert updates == [
        Update(
            update_id=1,
            message=Message(
                message_id=MessageID(1),
                date=0,
                chat=Chat(id=ChatID(1), type='private'),
                from_=User(id=UserID(1), is_bot=False, first_name='Test'),
            ),
        )
    ]
