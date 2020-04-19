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
class ChatPhoto:
    """Information for fetching the chat picture."""

    small_file_id: str
    small_file_unique_id: str  #don't know if changed or made by design
    big_file_id: str
    big_file_unique_id: str  #don't know if changed or made by design


# should this be private? (_ChatType)
class ChatType(Enum):
    """Chat type as atribute of the Chat class
    There is currently no functionality associated to this"""

    PRIVATE = 'private'
    GROUP = 'group'
    SUPERGROUP = 'supergroup'
    CHANNEL = 'channel'


@dataclass(frozen=True)
class ChatPermissions:
    """Describes actions that a non-administrator user is allowed to take in a chat."""

    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None


@dataclass(frozen=True)
class Chat:
    """Representation of a given chat."""

    id: ChatID
    type: ChatType
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    all_members_are_administrators: Optional[bool] = None
    photo: Optional[ChatPhoto] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    pinned_message: Optional[Message] = None
    permissions: Optional[ChatPermissions] = None
    slow_mode_delay: Optional[int] = None
    sticker_set_name: Optional[str] = None
    can_set_sticker_set: Optional[bool] = None


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
    user_id: Optional[int] = None # maybe use UserID here?
    vcard: Optional[str] = None


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
    foursquare_type: Optional[str] = None


# should this be private? (_PollType)
class PollType(Enum):
    """Poll type as atribute of the Poll class.
    There is currently no functionality associated to this."""

    REGULAR = 'regular'
    QUIZ = 'quiz'


@dataclass(frozen=True)
class PollOption:
    """Option/Answer for a Poll"""
    text: str
    voter_count: int


@dataclass(frozen=True)
class Poll:
    """Representation of a Poll."""

    id: str
    question: str
    options: List[PollOption] = None
    total_voter_count: int 
    is_closed: bool
    is_anonymous: bool
    type: PollType
    allows_multiple_answers: bool
    correct_option_id: Optional[int] = None


@dataclass(frozen=True)
class Dice:
    """Representation of a Dice"""

    value: int



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
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None
    telegram_payment_charge_id: str
    provider_payment_charge_id: str


# remember to reset previous 2 commits and then commit this one


@dataclass(frozen=True)
class MessageBase:
    """Base data for a Telegram message.
    this class exists to satisfy a particular specifity on reply_to_message and pinned_message
    arguments on the Message class: 
    Type Message: note that the Message object in this field will not contain further reply_to_message fields
    even if it itself is a reply."""

    message_id: MessageID
    date: int
    chat: Chat
    # Optional. Sender, empty for messages sent to channels
    # don't know if this should be ignored thou
    from_: Optional[User] = field(metadata={'rename': 'from'})
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_sender_name: Optional[str] = None
    forward_date: Optional[int] = None
    edit_date: Optional[int] = None
    media_group_id: Optional[str] = None
    author_signature: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    caption_entities: Optional[List[MessageEntity]] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    animation: Optional[Animation] = None
    game: Optional[Game] = None
    photo: Optional[List[PhotoSize]] = None
    sticker: Optional[Sticker] = None
    video: Optional[Video] = None
    voice: Optional[Voice] = None
    video_note: Optional[VideoNote] = None
    caption: Optional[str] = None
    contact: Optional[Contact] = None
    location: Optional[Location] = None
    venue: Optional[Venue] = None
    poll: Optional[Poll] = None
    dice: Optional[Dice] = None
    new_chat_members: Optional[List[User]] = None
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
    connected_website: Optional[str]
    # passport_data: Optional[PassportData] --> to be implemented
    # reply_markup: Optional[InlineKeyboardMarkup] --> to be implemented


@dataclass(frozen=True)
class Message(MessageBase):
    """Data for a Telegram message."""

    reply_to_message: Optional[MessageBase] = None
    pinned_message: Optional[MessageBase] = None


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
    """Parse mode for applying markup to text messages."""

    MARKDOWN = 'Markdown'
    HTML = 'HTML'


@dataclass(frozen=True)
class LoginURL:
    """A parameter of an inline keyboard button used to automatically authorize a user.
    """

    url: str
    forward_text: Optional[str] = None
    bot_username: Optional[str] = None
    request_write_access: Optional[bool] = None


@dataclass(frozen=True)
class KeyboardButtonPollType:
    """The type of a poll.

    The poll is allowed to be created and sent when the corresponding button is
    pressed.
    """

    type: str


@dataclass(frozen=True)
class KeyboardButton:
    """One button of the reply keyboard.

    At most one of the optional parameters can be present.
    """

    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None
    request_poll: Optional[KeyboardButtonPollType] = None


@dataclass(frozen=True)
class InlineKeyboardButton:
    """One button of an inline keyboard.

    At most one of the optional parameters can be present.
    """

    text: str
    url: Optional[str] = None
    login_url: Optional[LoginURL] = None
    callback_data: Optional[str] = None
    switch_inline_query: Optional[str] = None
    switch_inline_query_current_chat: Optional[str] = None
    callback_game: Optional[Any] = None
    pay: Optional[bool] = None


@dataclass(frozen=True)
class ReplyKeyboardMarkup:
    """A custom keyboard with reply options.

    At most one of the optional parameters can be present.
    """

    keyboard: List[List[KeyboardButton]]
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None
    selective: Optional[bool] = None


@dataclass(frozen=True)
class ReplyKeyboardRemove:
    """Request for a client to remove the custom current keyboard."""

    remove_keyboard: bool = field(default=True, init=False)
    selective: Optional[bool] = None


@dataclass(frozen=True)
class ForceReply:
    """Request for a client to display a reply interface to the user."""

    force_reply: bool = field(default=True, init=False)
    selective: Optional[bool] = None


ReplyMarkup = Union[
    InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
]


__all__ = [
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
