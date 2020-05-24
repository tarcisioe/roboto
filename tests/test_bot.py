"""Tests for the roboto.bot module."""
from io import BytesIO
from pathlib import Path
from typing import Tuple
from unittest.mock import MagicMock

import pytest

from roboto import (
    BotUser,
    Chat,
    ChatID,
    FileDescription,
    KeyboardButton,
    Message,
    MessageID,
    ReplyKeyboardMarkup,
    Token,
    Update,
    User,
    UserID,
)
from roboto.bot import BotAPI
from roboto.http_api import BytesMultipartData, IOMultipartData

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

    mocked_bot_api.request.assert_called_with(
        'get', path='/getMe', json=None,
    )

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

    mocked_bot_api.request.assert_called_with(
        'get', path='/getUpdates', json={'offset': 0}
    )

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

    mocked_bot_api.request.assert_called_with(
        'get', path='/getUpdates', json={'offset': 0}
    )

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


@pytest.mark.trio
async def test_send_message(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_message creates the correct payload and properly reads back
    the sent message.
    """
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    message = await mocked_bot_api.api.send_message(chat_id=ChatID(1), text='Hey.')

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendMessage', json={'chat_id': 1, 'text': 'Hey.'}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_message_with_reply_keyboard(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_message creates the correct payload with keyboard
    markup.
    """
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    message = await mocked_bot_api.api.send_message(
        chat_id=ChatID(1),
        text='Hey.',
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton('Bla.')]]),
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendMessage',
        json={
            'chat_id': 1,
            'text': 'Hey.',
            'reply_markup': '{"keyboard": [[{"text": "Bla."}]]}',
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_forward_message(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.forward_message properly reads the forwarded message."""
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 7,
            'date': 0,
            'chat': {
                'id': 2,
                'type': 'private',
                'username': 'johnsmith',
                'first_name': 'John',
                'last_name': 'Smith',
            },
            'from': {
                'id': 3,
                'is_bot': True,
                'first_name': 'Roboto Test Bot',
                'username': 'robototestbot',
            },
            'forward_from': {
                'id': 4,
                'is_bot': False,
                'first_name': 'John',
                'last_name': 'Smith',
                'username': 'johnsmith',
                'language_code': 'en',
            },
            'forward_date': 1,
            'text': 'test',
        },
    }

    message = await mocked_bot_api.api.forward_message(
        chat_id=ChatID(1), from_chat_id=ChatID(1), message_id=MessageID(1)
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/forwardMessage',
        json={'chat_id': 1, 'from_chat_id': 1, 'message_id': 1},
    )

    assert message == Message(
        message_id=MessageID(7),
        date=0,
        chat=Chat(
            id=ChatID(2),
            type='private',
            username='johnsmith',
            first_name='John',
            last_name='Smith',
        ),
        from_=User(
            id=UserID(3),
            is_bot=True,
            first_name='Roboto Test Bot',
            username='robototestbot',
        ),
        forward_from=User(
            id=UserID(4),
            is_bot=False,
            first_name='John',
            last_name='Smith',
            username='johnsmith',
            language_code='en',
        ),
        forward_date=1,
        text='test',
    )


@pytest.mark.trio
async def test_send_photo_with_path(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_message properly reads back the sent message."""
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    path = Path('dummy.jpg')

    message = await mocked_bot_api.api.send_photo(chat_id=ChatID(1), photo=path)

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendPhoto', multipart={'chat_id': 1, 'photo': path}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_photo_with_bytes(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_message properly reads back the sent message."""
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    message = await mocked_bot_api.api.send_photo(
        chat_id=ChatID(1),
        photo=FileDescription(b'dummy', mime_type='image/jpeg', basename='image.jpg'),
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendPhoto',
        multipart={
            'chat_id': 1,
            'photo': BytesMultipartData(
                b'dummy', mime_type='image/jpeg', basename='image.jpg'
            ),
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_photo_with_buffered_io(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_message properly reads back the sent message."""
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    bytes_io = BytesIO(b'dummy')

    message = await mocked_bot_api.api.send_photo(
        chat_id=ChatID(1),
        photo=FileDescription(bytes_io, mime_type='image/jpeg', basename='image.jpg'),
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendPhoto',
        multipart={
            'chat_id': 1,
            'photo': IOMultipartData(
                bytes_io, mime_type='image/jpeg', basename='image.jpg'
            ),
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_audio_with_path(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_audio creates the correct payload and properly reads
    back the returned message.
    """
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    path = Path('dummy.wav')

    message = await mocked_bot_api.api.send_audio(chat_id=ChatID(1), audio=path)

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendAudio', multipart={'chat_id': 1, 'audio': path}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_document_with_path(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_document creates the correct payload and properly reads
    back the returned message.
    """
    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    path = Path('dummy.pdf')

    message = await mocked_bot_api.api.send_document(chat_id=ChatID(1), document=path)

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendDocument', multipart={'chat_id': 1, 'document': path}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_video_with_path(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_video creates the correct payload and properly reads back
    the returned message.
    """

    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    path = Path('dummy.mp4')

    message = await mocked_bot_api.api.send_video(chat_id=ChatID(1), video=path)

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendVideo', multipart={'chat_id': 1, 'video': path}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_animation_with_path(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_animation creates the correct payload and properly reads
    back the returned message.
    """

    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
        },
    }

    path = Path('dummy.mp4')

    message = await mocked_bot_api.api.send_animation(chat_id=ChatID(1), animation=path)

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendAnimation', multipart={'chat_id': 1, 'animation': path}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )
