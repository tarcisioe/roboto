"""Types representing the bodies of API requests."""
import json
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar, Union, cast

from .api_types import ChatID, InputFile, MessageID, ParseMode, ReplyMarkup
from .datautil import to_json

T = TypeVar('T')


class JSONSerialized(str, Generic[T]):
    """Strong type for the JSON serialized version of a type."""


def json_serialize(value: Optional[T]) -> Optional[JSONSerialized[T]]:
    """Serialize value to its strong-typed JSON string type."""
    if value is None:
        return None

    return cast(JSONSerialized[T], json.dumps(to_json(value)))


@dataclass(frozen=True)
class GetUpdatesRequest:
    """Parameters for getting updates for a bot."""

    offset: Optional[int] = None
    limit: Optional[int] = None
    timeout: Optional[int] = None
    allowed_updates: Optional[List[str]] = None


@dataclass(frozen=True)
class SendMessageRequest:
    """Parameters for sending a message."""

    chat_id: Union[ChatID, str]
    text: str
    parse_mode: Optional[ParseMode] = None
    disable_web_page_preview: Optional[bool] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class ForwardMessageRequest:
    """Parameters for forwarding a message."""

    chat_id: Union[ChatID, str]
    from_chat_id: Union[ChatID, str]
    message_id: MessageID
    disable_notification: Optional[bool] = None


@dataclass(frozen=True)
class SendPhotoRequest:
    """Parameters for sending a photo."""

    chat_id: Union[ChatID, str]
    photo: InputFile
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendAudioRequest:
    """Parameters for sending an audio."""

    chat_id: Union[ChatID, str]
    audio: InputFile
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None
    thumb: Optional[InputFile] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None
