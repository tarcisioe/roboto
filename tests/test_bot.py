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
    InlineMessageID,
    InputMediaPhoto,
    InputMediaVideo,
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
from roboto.http_api import MultipartData

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
    """Test that BotAPI.forward_message creates the correct payload and properly reads
    back the sent message.
    """
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
    """Test that BotAPI.send_photo creates the correct payload and properly reads
    back the returned message when using a Path object as input.
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
    """Test that BotAPI.send_photo creates the correct payload and properly reads
    back the returned message when using bytes as input.
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

    message = await mocked_bot_api.api.send_photo(
        chat_id=ChatID(1),
        photo=FileDescription(b'dummy', mime_type='image/jpeg', basename='image.jpg'),
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendPhoto',
        multipart={
            'chat_id': 1,
            'photo': MultipartData(
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
    """Test that BotAPI.send_photo creates the correct payload and properly reads
    back the returned message when using a BufferedIO as input.
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
            'photo': MultipartData(
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
async def test_send_audio(mocked_bot_api: MockedBotAPI):
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
async def test_send_document(mocked_bot_api: MockedBotAPI):
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
async def test_send_video(mocked_bot_api: MockedBotAPI):
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
async def test_send_animation(mocked_bot_api: MockedBotAPI):
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


@pytest.mark.trio
async def test_send_voice(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_voice creates the correct payload and properly reads back
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

    path = Path('dummy.ogg')

    message = await mocked_bot_api.api.send_voice(chat_id=ChatID(1), voice=path)

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendVoice', multipart={'chat_id': 1, 'voice': path}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_video_note(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_video_note creates the correct payload and properly reads
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

    message = await mocked_bot_api.api.send_video_note(
        chat_id=ChatID(1), video_note=path
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendVideoNote', multipart={'chat_id': 1, 'video_note': path}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_media_group(mocker, mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_media_group creates the correct payload and properly reads
    back the returned message list.
    """

    uuid_mock = mocker.MagicMock()
    uuid_mock.side_effect = ['DUMMY-UUID-1', 'DUMMY-UUID-2']
    mocker.patch('roboto.media.uuid4', uuid_mock)

    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': [
            {
                'message_id': 1,
                'date': 0,
                'chat': {'id': 1, 'type': 'private'},
                'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
            }
        ],
    }

    photo_path = Path('dummy.jpg')
    video_path = Path('dummy.mp4')

    message = await mocked_bot_api.api.send_media_group(
        chat_id=ChatID(1),
        media=[InputMediaPhoto(photo_path), InputMediaVideo(video_path)],
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendMediaGroup',
        multipart={
            'attachedDUMMY-UUID-1': MultipartData(
                photo_path, mime_type='image/jpeg', basename='attachedDUMMY-UUID-1',
            ),
            'attachedDUMMY-UUID-2': MultipartData(
                video_path, mime_type='video/mp4', basename='attachedDUMMY-UUID-2',
            ),
            'chat_id': 1,
            'media': (
                '[{"media": "attach://attachedDUMMY-UUID-1", "type": "photo"}, '
                '{"media": "attach://attachedDUMMY-UUID-2", "type": "video"}]'
            ),
        },
    )

    assert message == [
        Message(
            message_id=MessageID(1),
            date=0,
            chat=Chat(id=ChatID(1), type='private'),
            from_=User(id=UserID(1), is_bot=True, first_name='Test'),
        )
    ]


@pytest.mark.trio
async def test_send_location(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_location creates the correct payload and properly reads
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

    message = await mocked_bot_api.api.send_location(
        chat_id=ChatID(1), latitude=35.716692, longitude=139.785962,
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendLocation',
        json={'chat_id': 1, 'latitude': 35.716692, 'longitude': 139.785962},
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_edit_message_live_location(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.edit_message_live_location creates the correct payload
    and properly reads back the returned message.
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

    message = await mocked_bot_api.api.edit_message_live_location(
        chat_id=ChatID(1),
        message_id=MessageID(1),
        latitude=35.716692,
        longitude=139.785962,
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/editMessageLiveLocation',
        json={
            'chat_id': 1,
            'message_id': 1,
            'latitude': 35.716692,
            'longitude': 139.785962,
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_edit_inline_message_live_location(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.edit_inline_message_live_location creates the correct payload
    and properly reads back the returned message.
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

    message = await mocked_bot_api.api.edit_inline_message_live_location(
        inline_message_id=InlineMessageID('abc'),
        latitude=35.716692,
        longitude=139.785962,
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/editMessageLiveLocation',
        json={
            'inline_message_id': 'abc',
            'latitude': 35.716692,
            'longitude': 139.785962,
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_stop_message_live_location(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.stop_message_live_location creates the correct payload
    and properly reads back the returned message.
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

    message = await mocked_bot_api.api.stop_message_live_location(
        chat_id=ChatID(1), message_id=MessageID(1),
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/stopMessageLiveLocation', json={'chat_id': 1, 'message_id': 1},
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_stop_inline_message_live_location(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.stop_inline_message_live_location creates the correct payload
    and properly reads back the returned message.
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

    message = await mocked_bot_api.api.stop_inline_message_live_location(
        inline_message_id=InlineMessageID('abc'),
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/stopMessageLiveLocation', json={'inline_message_id': 'abc'}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_venue(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_venue creates the correct payload and properly reads
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

    message = await mocked_bot_api.api.send_venue(
        chat_id=ChatID(1),
        latitude=35.716692,
        longitude=139.785962,
        title='Yanagibayashi Shrine',
        address='3 Chome-10-7 Matsugaya',
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendVenue',
        json={
            'chat_id': 1,
            'latitude': 35.716692,
            'longitude': 139.785962,
            'title': 'Yanagibayashi Shrine',
            'address': '3 Chome-10-7 Matsugaya',
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_send_contact(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_contact creates the correct payload and properly reads
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

    message = await mocked_bot_api.api.send_contact(
        chat_id=ChatID(1),
        phone_number='01189998819991197253',
        first_name='Emergency',
        last_name='Services',
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendContact',
        json={
            'chat_id': 1,
            'phone_number': '01189998819991197253',
            'first_name': 'Emergency',
            'last_name': 'Services',
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )
