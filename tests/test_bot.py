"""Tests for the roboto.bot module."""
from io import BytesIO
from pathlib import Path
from typing import Tuple
from unittest.mock import MagicMock

import pytest

from roboto import (
    BotUser,
    Chat,
    ChatAction,
    ChatID,
    ChatPermissions,
    Dice,
    DiceEmoji,
    File,
    FileDescription,
    FileID,
    InlineMessageID,
    InputMediaPhoto,
    InputMediaVideo,
    KeyboardButton,
    Message,
    MessageID,
    Poll,
    PollID,
    PollOption,
    PollType,
    ReplyKeyboardMarkup,
    Token,
    Update,
    User,
    UserID,
    UserProfilePhotos,
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


@pytest.mark.trio
async def test_send_poll(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_poll creates the correct payload and properly reads
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

    message = await mocked_bot_api.api.send_poll(
        chat_id=ChatID(1),
        question='How many roads must a man walk down?',
        options=['01189998819991197253', '42', 'Before you can call him a man?'],
        poll_type=PollType.QUIZ,
        correct_option_id=1,
        is_anonymous=False,
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/sendPoll',
        json={
            'chat_id': 1,
            'question': 'How many roads must a man walk down?',
            'options': (
                '["01189998819991197253", "42", "Before you can call him a man?"]'
            ),
            'is_anonymous': False,
            'type': 'quiz',
            'correct_option_id': 1,
        },
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
    )


@pytest.mark.trio
async def test_stop_poll(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.stop_poll creates the correct payload and properly reads
    back the returned poll.
    """

    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'id': '1',
            'question': 'How many roads must a man walk down?',
            'options': [
                {'text': '01189998819991197253', 'voter_count': 0},
                {'text': '42', 'voter_count': 1},
                {'text': 'Before you can call him a man?', 'voter_count': 0},
            ],
            'total_voter_count': 0,
            'is_closed': True,
            'is_anonymous': False,
            'type': 'quiz',
            'allows_multiple_answers': False,
            'correct_option_id': 1,
        },
    }

    poll = await mocked_bot_api.api.stop_poll(
        chat_id=ChatID(1), message_id=MessageID(1),
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/stopPoll', json={'chat_id': 1, 'message_id': 1},
    )

    assert poll == Poll(
        id=PollID('1'),
        question='How many roads must a man walk down?',
        options=[
            PollOption(text='01189998819991197253', voter_count=0),
            PollOption(text='42', voter_count=1),
            PollOption(text='Before you can call him a man?', voter_count=0),
        ],
        total_voter_count=0,
        is_closed=True,
        is_anonymous=False,
        type='quiz',
        allows_multiple_answers=False,
        correct_option_id=1,
        explanation=None,
        explanation_entities=None,
        open_period=None,
        close_date=None,
    )


@pytest.mark.trio
async def test_send_dice(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_dice creates the correct payload and properly reads
    back the returned message.
    """

    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'message_id': 1,
            'date': 0,
            'chat': {'id': 1, 'type': 'private'},
            'from': {'id': 1, 'is_bot': True, 'first_name': 'Test'},
            'dice': {'emoji': '🎯', 'value': 6},
        },
    }

    message = await mocked_bot_api.api.send_dice(
        chat_id=ChatID(1), emoji=DiceEmoji.DART
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendDice', json={'chat_id': 1, 'emoji': '🎯'}
    )

    assert message == Message(
        message_id=MessageID(1),
        date=0,
        chat=Chat(id=ChatID(1), type='private'),
        from_=User(id=UserID(1), is_bot=True, first_name='Test'),
        dice=Dice(emoji='🎯', value=6),
    )


@pytest.mark.trio
async def test_send_chat_action(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.send_chat_action creates the correct payload and properly reads
    back the returned boolean.
    """

    mocked_bot_api.response.json.return_value = {'ok': True, 'result': True}

    result = await mocked_bot_api.api.send_chat_action(
        chat_id=ChatID(1), action=ChatAction.UPLOAD_AUDIO,
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/sendChatAction', json={'chat_id': 1, 'action': 'upload_audio'},
    )

    assert result


@pytest.mark.trio
async def test_get_user_profile_photos(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.get_user_profile_photos creates the correct payload and properly
    reads back the returned user profile photos.
    """

    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {'total_count': 0, 'photos': []},
    }

    result = await mocked_bot_api.api.get_user_profile_photos(user_id=UserID(1))

    mocked_bot_api.request.assert_called_with(
        'post', path='/getUserProfilePhotos', json={'user_id': 1},
    )

    assert result == UserProfilePhotos(total_count=0, photos=[])


@pytest.mark.trio
async def test_get_file(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.get_file creates the correct payload and properly reads
    back the returned file.
    """

    mocked_bot_api.response.json.return_value = {
        'ok': True,
        'result': {
            'file_id': (
                'AgACAgQAAxkDAAPIXt2uWLhlNVKKIJVNlb0bFrnPCNMAAla'
                'oMRsGCZxQ96KmYduqAAE-QmygGgAEAQADAgADcwADrcoFAAEaBA'
            ),
            'file_unique_id': 'AQADQmygGgAErcoFAAE',
            'file_size': 1018,
            'file_path': 'photos/file_0.jpg',
        },
    }

    result = await mocked_bot_api.api.get_file(
        file_id=FileID(
            'AgACAgQAAxkDAAPIXt2uWLhlNVKKIJVNlb0bFrnPCNMAAla'
            'oMRsGCZxQ96KmYduqAAE-QmygGgAEAQADAgADcwADrcoFAAEaBA'
        ),
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/getFile',
        json={
            'file_id': (
                'AgACAgQAAxkDAAPIXt2uWLhlNVKKIJVNlb0bFrnPCNMAAla'
                'oMRsGCZxQ96KmYduqAAE-QmygGgAEAQADAgADcwADrcoFAAEaBA'
            ),
        },
    )

    assert result == File(
        file_id=FileID(
            'AgACAgQAAxkDAAPIXt2uWLhlNVKKIJVNlb0bFrnPCNMAAla'
            'oMRsGCZxQ96KmYduqAAE-QmygGgAEAQADAgADcwADrcoFAAEaBA'
        ),
        file_unique_id=FileID('AQADQmygGgAErcoFAAE'),
        file_size=1018,
        file_path='photos/file_0.jpg',
    )


@pytest.mark.trio
async def test_kick_chat_member(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.kick_chat_member creates the correct payload and properly reads
    back the returned bool.
    """

    mocked_bot_api.response.json.return_value = {'ok': True, 'result': True}

    result = await mocked_bot_api.api.kick_chat_member(
        chat_id=ChatID(1), user_id=UserID(1),
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/kickChatMember', json={'chat_id': 1, 'user_id': 1},
    )

    assert result


@pytest.mark.trio
async def test_unban_chat_member(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.unban_chat_member creates the correct payload and properly reads
    back the returned bool.
    """

    mocked_bot_api.response.json.return_value = {'ok': True, 'result': True}

    result = await mocked_bot_api.api.unban_chat_member(
        chat_id=ChatID(1), user_id=UserID(1),
    )

    mocked_bot_api.request.assert_called_with(
        'post', path='/unbanChatMember', json={'chat_id': 1, 'user_id': 1},
    )

    assert result


@pytest.mark.trio
async def test_restrict_chat_member(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.restrict_chat_member creates the correct payload and
    properly reads back the returned bool.
    """

    mocked_bot_api.response.json.return_value = {'ok': True, 'result': True}

    result = await mocked_bot_api.api.restrict_chat_member(
        chat_id=ChatID(1),
        user_id=UserID(1),
        permissions=ChatPermissions(can_change_info=False),
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/restrictChatMember',
        json={'chat_id': 1, 'user_id': 1, 'permissions': '{"can_change_info": false}'},
    )

    assert result


@pytest.mark.trio
async def test_promote_chat_member(mocked_bot_api: MockedBotAPI):
    """Test that BotAPI.promote_chat_member creates the correct payload and
    properly reads back the returned bool.
    """

    mocked_bot_api.response.json.return_value = {'ok': True, 'result': True}

    result = await mocked_bot_api.api.promote_chat_member(
        chat_id=ChatID(1), user_id=UserID(1), can_pin_messages=True,
    )

    mocked_bot_api.request.assert_called_with(
        'post',
        path='/promoteChatMember',
        json={'chat_id': 1, 'user_id': 1, 'can_pin_messages': True},
    )

    assert result
