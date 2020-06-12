"""Roboto's strong types and aggregates."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import BinaryIO, List, NewType, Optional, Union

from typing_extensions import Literal

from .url import URL

Token = NewType('Token', str)
UserID = NewType('UserID', int)
ChatID = NewType('ChatID', int)
MessageID = NewType('MessageID', int)
InlineMessageID = NewType('InlineMessageID', str)
FileID = NewType('FileID', str)
PollID = NewType('PollID', str)
CallbackQueryID = NewType('CallbackQueryID', str)


@dataclass(frozen=True)
class FileDescription:
    """Describe a file to be sent through the API with customized metadata."""

    binary_source: Union[Path, BinaryIO, bytes]
    basename: str
    mime_type: str = 'application/octet-stream'


# pylint: disable=invalid-triple-quote
InputFile = Union[Path, BinaryIO, FileID, FileDescription, URL]
"""An InputFile can be either:

A Path object: This will be used to open the file and read it to send.
A BufferedIOBase object: This supports sending an already open file.
A FileID from Telegram's Bot API itself: This will just send a previously sent file.
A FileDescription object: This is used to send binary data directly as a file, or to
                          customize mimetype or filename.
A URL: This instructs Telegram's server to download the file and send it. In
       this case, file size is severely limited.

Refer to https://core.telegram.org/bots/api#sending-files for more information.
"""
# pylint: enable=invalid-triple-quote


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
    """A user returned by the Bot API."""


@dataclass(frozen=True)
class BotUser(_UserOptionalCommon, _BotUserRequired):
    """A Bot user returned by the Bot API (only through getMe)."""


@dataclass(frozen=True)
class ChatPhoto:
    """Information for fetching the chat picture."""

    small_file_id: FileID
    small_file_unique_id: FileID
    big_file_id: FileID
    big_file_unique_id: FileID


@dataclass(frozen=True)
class ChatMember:
    """Information about one member of a chat."""

    user: User
    status: str
    custom_title: Optional[str] = None
    until_date: Optional[int] = None
    can_be_edited: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    is_member: Optional[bool] = None
    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None


@dataclass(frozen=True)
class ChatPermissions:
    """Actions that a non-administrator user is allowed to take in a chat."""

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
    type: str
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
    language: Optional[str] = None


@dataclass(frozen=True)
class PhotoSize:
    """Data about an image size both in pixels and bytes."""

    file_id: FileID
    file_unique_id: FileID
    width: int
    height: int
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Audio:
    """Metadata about an audio message."""

    file_id: FileID
    file_unique_id: FileID
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    thumb: Optional[PhotoSize] = None


@dataclass(frozen=True)
class Document:
    """Metadata about a generic file."""

    file_id: FileID
    file_unique_id: FileID
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class Animation:
    """Metadata about a message with an animation (gif, mp4)."""

    file_id: FileID
    file_unique_id: FileID
    width: int
    height: int
    duration: int
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
    file_unique_id: FileID
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
    file_unique_id: FileID
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass(frozen=True)
class VideoNote:
    """Metadata on a video note."""

    file_id: FileID
    file_unique_id: FileID
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
    user_id: Optional[UserID] = None
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


@dataclass(frozen=True)
class PollOption:
    """Option/Answer for a Poll"""

    text: str
    voter_count: int


@dataclass(frozen=True)
class PollAnswer:
    """An answer of a user in a non-anonymous poll."""

    poll_id: str
    user: User
    option_ids: List[int]


class PollType(Enum):
    """The type of a poll."""

    QUIZ = 'quiz'
    REGULAR = 'regular'


@dataclass(frozen=True)
class Poll:
    """Representation of a Poll."""

    id: PollID
    question: str
    options: List[PollOption]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    explanation_entities: Optional[List[MessageEntity]] = None
    open_period: Optional[int] = None
    close_date: Optional[int] = None


class DiceEmoji(Enum):
    """Supported emojis for sending Dice messages."""

    DICE = '🎲'
    DART = '🎯'
    BASKETBALL = '🏀'


@dataclass(frozen=True)
class Dice:
    """Representation of a Dice"""

    emoji: str
    value: int


@dataclass(frozen=True)
class UserProfilePhotos:
    """A user's profile pictures."""

    total_count: int
    photos: List[List[PhotoSize]]


@dataclass(frozen=True)
class File:
    """A file ready to be downloaded."""

    file_id: FileID
    file_unique_id: FileID
    file_size: Optional[int]
    file_path: Optional[str]


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
class PassportData:
    """Information about Telegram Passport data shared with the bot by the user."""

    data: List[EncryptedPassportElement]
    credentials: EncryptedCredentials


@dataclass(frozen=True)
class PassportFile:
    """A file uploaded to Telegram Passport.

    Currently all Telegram Passport files are in JPEG format when decrypted
    and don't exceed 10MB.
    """

    file_id: str
    file_unique_id: str
    file_size: int
    file_date: int


@dataclass(frozen=True)
class EncryptedPassportElement:
    """Information about Telegram Passport elements shared with the bot by the user."""

    type: str
    hash: str
    data: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    files: Optional[List[PassportFile]] = None
    front_side: Optional[PassportFile] = None
    reverse_side: Optional[PassportFile] = None
    selfie: Optional[PassportFile] = None
    translation: Optional[List[PassportFile]] = None


@dataclass(frozen=True)
class EncryptedCredentials:
    """Data required for decrypting and authenticating EncryptedPassportElement.

    See the Telegram Passport Documentation for a complete description of the
    data decryption and authentication processes.
    """

    data: str
    hash: str
    secret: str


@dataclass(frozen=True)
class InlineKeyboardMarkup:
    """Represents an inline keyboard that appears next to the message it belongs to."""

    inline_keyboard: List[List[InlineKeyboardButton]]


@dataclass(frozen=True)
class InlineKeyboardButton:
    """One button of an inline keyboard.

    You must use exactly one of the optional fields.
    """

    text: str
    url: Optional[str] = None
    login_url: Optional[LoginUrl] = None
    callback_data: Optional[str] = None
    switch_inline_query: Optional[str] = None
    switch_inline_query_current_chat: Optional[str] = None
    callback_game: Optional[CallbackGame] = None
    pay: Optional[bool] = None


@dataclass(frozen=True)
class CallbackGame:
    """A placeholder, currently holds no information."""


@dataclass(frozen=True)
class _MessageBase:
    """Base data for a Telegram Message.

    This class is made this way to permit
    MessageWithNoReply and Message to have no inheritance relationship
    """

    message_id: MessageID
    date: int
    chat: Chat
    from_: Optional[User] = field(metadata={'rename': 'from'})
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_sender_name: Optional[str] = None
    forward_date: Optional[int] = None
    via_bot: Optional[User] = None
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
    connected_website: Optional[str] = None
    passport_data: Optional[PassportData] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None


@dataclass(frozen=True)
class MessageWithNoReply(_MessageBase):
    """ A Message object without reply_to_message and pinned_message.

    This class exists to satisfy a particular specifity on
    reply_to_message and pinned_message arguments on the Message class {
        Type Message, note that the Message object in this field will not
        contain further reply_to_message fields even if it itself is a reply.
    }
    """


@dataclass(frozen=True)
class Message(_MessageBase):
    """Data for a Telegram message."""

    reply_to_message: Optional[MessageWithNoReply] = None
    pinned_message: Optional[MessageWithNoReply] = None


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

    id: CallbackQueryID
    from_: User = field(metadata={'rename': 'from'})
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    chat_instance: Optional[str] = None
    data: Optional[str] = None
    game_short_name: Optional[str] = None


@dataclass(frozen=True)
class ShippingQuery:
    """An incoming shipping query."""

    id: str
    invoide_payload: str
    shipping_address: ShippingAddress
    from_: User = field(metadata={'rename': 'from'})


@dataclass(frozen=True)
class PreCheckoutQuery:
    """An incoming pre-checkout query."""

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


@dataclass(frozen=True)
class BotCommand:
    """This object represents a bot command."""

    command: str
    description: str


@dataclass(frozen=True)
class ResponseParameters:
    """Information about why a request was unsuccessful."""

    migrate_to_chat_id: Optional[int]
    retry_after: Optional[int]


@dataclass(frozen=True)
class InputMediaPhoto:
    """A photo to be sent."""

    media: InputFile
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    type: Literal['photo'] = field(default='photo', init=False)


@dataclass(frozen=True)
class InputMediaVideo:
    """The content of a media message to be sent.

    Can be of type: Animation, Document, Audio, Photo and Video.
    """

    media: InputFile
    thumb: Optional[Union[URL, FileID]] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    supports_streaming: Optional[bool] = None
    type: Literal['video'] = field(default='video', init=False)


@dataclass(frozen=True)
class InputMediaAnimation:
    """The content of a media message to be sent.

    Can be of type: Animation, Document, Audio, Photo and Video.
    """

    media: InputFile
    thumb: Optional[Union[URL, FileID]] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    type: Literal['animation'] = field(default='animation', init=False)


@dataclass(frozen=True)
class InputMediaAudio:
    """The content of a media message to be sent.

    Can be of type: Animation, Document, Audio, Photo and Video.
    """

    media: InputFile
    thumb: Optional[Union[URL, FileID]] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None
    type: Literal['animation'] = field(default='animation', init=False)


@dataclass(frozen=True)
class InputMediaDocument:
    """A photo to be sent."""

    media: InputFile
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    thumb: Optional[Union[URL, FileID]] = None
    type: Literal['document'] = field(default='document', init=False)


InputMedia = Union[
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
]


class ParseMode(Enum):
    """Parse mode for applying markup to text messages."""

    MARKDOWN = 'Markdown'
    HTML = 'HTML'


@dataclass(frozen=True)
class LoginUrl:
    """A parameter used to automatically authorize a user.

    Used in inline keyboard buttons.
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
    InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
]


class ChatAction(Enum):
    """Actions to display to show that the bot is doing something before sending."""

    TYPING = 'typing'
    UPLOAD_PHOTO = 'upload_photo'
    RECORD_VIDEO = 'record_video'
    UPLOAD_VIDEO = 'upload_video'
    RECORD_AUDIO = 'record_audio'
    UPLOAD_AUDIO = 'upload_audio'
    UPLOAD_DOCUMENT = 'upload_document'
    FIND_LOCATION = 'find_location'
    RECORD_VIDEO_NOTE = 'record_video_note'
    UPLOAD_VIDEO_NOTE = 'upload_video_note'


__all__ = [
    'Animation',
    'Audio',
    'BotCommand',
    'BotUser',
    'CallbackGame',
    'CallbackQuery',
    'CallbackQueryID',
    'Chat',
    'ChatAction',
    'ChatID',
    'ChatMember',
    'ChatPermissions',
    'ChatPhoto',
    'ChosenInlineResult',
    'Contact',
    'Dice',
    'DiceEmoji',
    'Document',
    'EncryptedCredentials',
    'EncryptedPassportElement',
    'File',
    'FileDescription',
    'FileID',
    'ForceReply',
    'Game',
    'InlineKeyboardButton',
    'InlineKeyboardMarkup',
    'InlineMessageID',
    'InlineQuery',
    'InputMedia',
    'InputMediaAnimation',
    'InputMediaAudio',
    'InputMediaDocument',
    'InputMediaPhoto',
    'InputMediaVideo',
    'InputFile',
    'Invoice',
    'KeyboardButton',
    'KeyboardButtonPollType',
    'Location',
    'LoginUrl',
    'MaskPosition',
    'Message',
    'MessageWithNoReply',
    'MessageEntity',
    'MessageID',
    'OrderInfo',
    'ParseMode',
    'PassportData',
    'PassportFile',
    'PhotoSize',
    'Poll',
    'PollAnswer',
    'PollID',
    'PollOption',
    'PollType',
    'PreCheckoutQuery',
    'ReplyMarkup',
    'ReplyKeyboardMarkup',
    'ReplyKeyboardRemove',
    'ResponseParameters',
    'ShippingAddress',
    'ShippingQuery',
    'Sticker',
    'SuccessfulPayment',
    'Token',
    'Update',
    'User',
    'UserID',
    'UserProfilePhotos',
    'Venue',
    'Video',
    'VideoNote',
    'Voice',
]
