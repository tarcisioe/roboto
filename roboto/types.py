"""Roboto's strong types and aggregates."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, NewType, Optional, Union

Token = NewType('Token', str)
UserID = NewType('UserID', int)
ChatID = NewType('ChatID', int)
MessageID = NewType('MessageID', int)
FileID = NewType('FileID', str)


@dataclass(frozen=True)
class _UserRequiredCommon:
    id: UserID
    is_bot: bool
    first_name: str


@dataclass(frozen=True)
class _BotUserRequired(_UserRequiredCommon):
    can_join_groups: bool
    can_read_all_group_messages: bool
    supports_inline_queries: bool


@dataclass(frozen=True)
class _UserOptionalCommon:
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


@dataclass(frozen=True)
class User(_UserOptionalCommon, _UserRequiredCommon):
    """Representation of a user returned by the Bot API."""


@dataclass(frozen=True)
class BotUser(_UserOptionalCommon, _BotUserRequired):
    """Representation of a Bot user returned by the Bot API through getMe."""


@dataclass(frozen=True)
class APIResponse:
    """API Response format."""

    ok: bool
    result: Optional[Any] = None
    error_code: Optional[int] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class ChatPhoto:
    """Information for fetching the chat picture."""

    small_file_id: str
    big_file_id: str


@dataclass(frozen=True)
class Chat:
    """Representation of a given chat."""

    id: ChatID
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    all_members_are_administrators: Optional[bool] = None
    photo: Optional[ChatPhoto] = None
    descriptions: Optional[str] = None
    invite_link: Optional[str] = None


@dataclass(frozen=True)
class MessageEntity:
    """An entity inside a message (hashtags, links...)"""

    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None


@dataclass(frozen=True)
class PhotoSize:
    """Data about an image size both in pixels and bytes."""

    file_id: FileID
    width: int
    height: int
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Audio:
    """Metadata about an audio message."""

    file_id: FileID
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Document:
    """Metadata about a generic file."""

    file_id: FileID
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[str] = None


@dataclass(frozen=True)
class Animation:
    """Metadata about a message with an animation (gif, mp4)."""

    file_id: FileID
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Game:
    """Data about a Telegram Game."""

    title: str
    description: str
    photo: List[PhotoSize]
    text: Optional[str] = None
    text_entities: Optional[List[MessageEntity]] = None
    animation: Optional[Animation] = None


@dataclass(frozen=True)
class MaskPosition:
    """Information about where to put a mask on a face."""

    point: str
    x_shift: float
    y_shift: float
    scale: float


@dataclass(frozen=True)
class Sticker:
    """Metadata about a given sticker."""

    file_id: FileID
    width: int
    height: int
    thumb: Optional[PhotoSize] = None
    emoji: Optional[str] = None
    set_name: Optional[str] = None
    mask_position: Optional[MaskPosition] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Video:
    """Metadata about a video message."""

    file_id: FileID
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Voice:
    """Metadata about a voice message."""

    file_id: FileID
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class VideoNote:
    """Metadata on a video note."""

    file_id: FileID
    length: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Contact:
    """Representation of a contact."""

    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None


@dataclass(frozen=True)
class Location:
    """A GPS location."""

    longitude: float
    latitude: float


@dataclass(frozen=True)
class Venue:
    """A venue on Foursquare."""

    location: Location
    title: str
    address: str
    foursquare_id: Optional[str] = None


@dataclass(frozen=True)
class Invoice:
    """A billing invoice."""

    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


@dataclass(frozen=True)
class ShippingAddress:
    """An address for online purchases."""

    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


@dataclass(frozen=True)
class OrderInfo:
    """Information about an order."""

    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[ShippingAddress] = None


@dataclass(frozen=True)
class SuccessfulPayment:
    """Confirmation data for a successful payment."""

    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None


@dataclass(frozen=True)
class MessageBase:
    """Base data for a Telegram message."""

    message_id: MessageID
    date: int
    chat: Chat
    from_: User = field(metadata={'rename': 'from'})
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_date: Optional[int] = None
    edit_date: Optional[int] = None
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    game: Optional[Game] = None
    photo: Optional[List[PhotoSize]] = None
    sticker: Optional[Sticker] = None
    video: Optional[Video] = None
    voice: Optional[Voice] = None
    video_note: Optional[VideoNote] = None
    new_chat_members: Optional[List[User]] = None
    caption: Optional[str] = None
    contact: Optional[Contact] = None
    location: Optional[Location] = None
    venue: Optional[Venue] = None
    new_chat_member: Optional[User] = None
    left_chat_member: Optional[User] = None
    new_chat_title: Optional[str] = None
    new_chat_photo: Optional[List[PhotoSize]] = None
    delete_chat_photo: Optional[bool] = None
    group_chat_created: Optional[bool] = None
    supergroup_chat_created: Optional[bool] = None
    chat_channel_created: Optional[bool] = None
    migrate_to_chat_id: Optional[int] = None
    migrate_from_chat_id: Optional[int] = None
    invoice: Optional[Invoice] = None
    successful_payment: Optional[SuccessfulPayment] = None


@dataclass(frozen=True)
class Message:
    """Data for a Telegram message."""

    message_id: MessageID
    date: int
    chat: Chat
    from_: User = field(metadata={'rename': 'from'})
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_date: Optional[int] = None
    reply_to_message: Optional[MessageBase] = None
    edit_date: Optional[int] = None
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    game: Optional[Game] = None
    photo: Optional[List[PhotoSize]] = None
    sticker: Optional[Sticker] = None
    video: Optional[Video] = None
    voice: Optional[Voice] = None
    video_note: Optional[VideoNote] = None
    new_chat_members: Optional[List[User]] = None
    caption: Optional[str] = None
    contact: Optional[Contact] = None
    location: Optional[Location] = None
    venue: Optional[Venue] = None
    new_chat_member: Optional[User] = None
    left_chat_member: Optional[User] = None
    new_chat_title: Optional[str] = None
    new_chat_photo: Optional[List[PhotoSize]] = None
    delete_chat_photo: Optional[bool] = None
    group_chat_created: Optional[bool] = None
    supergroup_chat_created: Optional[bool] = None
    chat_channel_created: Optional[bool] = None
    migrate_to_chat_id: Optional[int] = None
    migrate_from_chat_id: Optional[int] = None
    pinned_message: Optional[MessageBase] = None
    invoice: Optional[Invoice] = None
    successful_payment: Optional[SuccessfulPayment] = None


@dataclass(frozen=True)
class InlineQuery:
    """An incoming inline query."""

    id: str
    query: str
    offset: str
    from_: User = field(metadata={'rename': 'from'})
    location: Optional[Location] = None


@dataclass(frozen=True)
class ChosenInlineResult:
    """The result of an inline query that was chosen by the user."""

    result_id: str
    query: str
    from_: User = field(metadata={'rename': 'from'})
    location: Optional[Location] = None
    inline_message_id: Optional[str] = None


@dataclass(frozen=True)
class CallbackQuery:
    """An incoming callback from an inline keyboard."""

    id: str
    from_: User = field(metadata={'rename': 'from'})
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    chat_instance: Optional[str] = None
    data: Optional[str] = None
    game_short_name: Optional[str] = None


@dataclass(frozen=True)
class ShippingQuery:
    """information about an incoming shipping query."""

    id: str
    invoide_payload: str
    shipping_address: ShippingAddress
    from_: User = field(metadata={'rename': 'from'})


@dataclass(frozen=True)
class PreCheckoutQuery:
    """Information about an incoming pre-checkout query."""

    id: str
    currency: str
    total_amount: int
    invoice_payload: str
    from_: User = field(metadata={'rename': 'from'})
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None


@dataclass(frozen=True)
class Update:
    """An update for the bot.

    At most one of the optional parameters can be present.
    """

    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    edited_channel_post: Optional[Message] = None
    inline_query: Optional[InlineQuery] = None
    chosen_inline_result: Optional[ChosenInlineResult] = None
    callback_query: Optional[CallbackQuery] = None
    shipping_query: Optional[ShippingQuery] = None
    pre_checkout_query: Optional[PreCheckoutQuery] = None


class ParseMode(Enum):
    """Parse mode for text messages."""

    MARKDOWN = 'Markdown'
    HTML = 'HTML'


@dataclass(frozen=True)
class SendMessageRequest:
    """Parameters for sending a message."""

    chat_id: Union[ChatID, str]
    text: str
    parse_mode: Optional[ParseMode] = None
    disable_web_page_preview: Optional[bool] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[str] = None


@dataclass(frozen=True)
class GetUpdatesRequest:
    """Parameters for getting updates for a bot."""

    offset: Optional[int] = None
    limit: Optional[int] = None
    timeout: Optional[int] = None
    allowed_updates: Optional[List[str]] = None


__all__ = [
    'APIResponse',
    'Animation',
    'Audio',
    'BotUser',
    'CallbackQuery',
    'Chat',
    'ChatID',
    'ChatPhoto',
    'ChosenInlineResult',
    'Contact',
    'Document',
    'FileID',
    'Game',
    'GetUpdatesRequest',
    'InlineQuery',
    'Invoice',
    'Location',
    'MaskPosition',
    'Message',
    'MessageBase',
    'MessageEntity',
    'MessageID',
    'OrderInfo',
    'ParseMode',
    'PhotoSize',
    'PreCheckoutQuery',
    'SendMessageRequest',
    'ShippingAddress',
    'ShippingQuery',
    'Sticker',
    'SuccessfulPayment',
    'Token',
    'Update',
    'User',
    'UserID',
    'Venue',
    'Video',
    'VideoNote',
    'Voice',
]
