"""Types representing the bodies of API requests."""
import json
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar, Union, cast

from .api_types import (
    BotCommand,
    CallbackQueryID,
    ChatAction,
    ChatID,
    ChatPermissions,
    DiceEmoji,
    FileID,
    InlineKeyboardMarkup,
    InlineMessageID,
    InputFile,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    MessageID,
    ParseMode,
    PollType,
    ReplyMarkup,
    UserID,
)
from .datautil import to_json_like

T = TypeVar('T')


class JSONSerialized(str, Generic[T]):
    """Strong type for the JSON serialized version of a type."""


def json_serialize(value: T) -> JSONSerialized[T]:
    """Serialize value to its strong-typed JSON string type."""
    return cast(JSONSerialized[T], json.dumps(to_json_like(value)))


def maybe_json_serialize(value: Optional[T]) -> Optional[JSONSerialized[T]]:
    """Serialize value to its strong-typed JSON string type."""
    if value is None:
        return None

    return json_serialize(value)


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


@dataclass(frozen=True)
class SendDocumentRequest:
    """Parameters for sending a document."""

    chat_id: Union[ChatID, str]
    document: InputFile
    thumb: Optional[InputFile] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendVideoRequest:
    """Parameters for sending a video."""

    chat_id: Union[ChatID, str]
    video: InputFile
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumb: Optional[InputFile] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    supports_streaming: Optional[bool] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendAnimationRequest:
    """Parameters for sending an animation."""

    chat_id: Union[ChatID, str]
    animation: InputFile
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumb: Optional[InputFile] = None
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendVoiceRequest:
    """Parameters for sending a voice note (OGG/OPUS audio)."""

    chat_id: Union[ChatID, str]
    voice: InputFile
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    duration: Optional[int] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendVideoNoteRequest:
    """Parameters for sending a video note (rounded square mp4 videos)."""

    chat_id: Union[ChatID, str]
    video_note: InputFile
    duration: Optional[int] = None
    length: Optional[int] = None
    thumb: Optional[InputFile] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendMediaGroupRequest:
    """Parameters for sending a group of photos or videos as an album."""

    chat_id: Union[ChatID, str]
    media: JSONSerialized[List[Union[InputMediaPhoto, InputMediaVideo]]]
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None


@dataclass(frozen=True)
class SendLocationRequest:
    """Parameters for sending a point on the map."""

    chat_id: Union[ChatID, str]
    latitude: float
    longitude: float
    live_period: Optional[int] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditMessageLiveLocationRequest:
    """Parameters for editing a live location non-inline message."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    latitude: float
    longitude: float
    reply_markup: Optional[JSONSerialized[InlineKeyboardMarkup]] = None


@dataclass(frozen=True)
class EditInlineMessageLiveLocationRequest:
    """Parameters for editing a live location inline message."""

    inline_message_id: InlineMessageID
    latitude: float
    longitude: float
    reply_markup: Optional[JSONSerialized[InlineKeyboardMarkup]] = None


@dataclass(frozen=True)
class StopMessageLiveLocationRequest:
    """Parameters for stopping a live location non-inline message."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    reply_markup: Optional[JSONSerialized[InlineKeyboardMarkup]] = None


@dataclass(frozen=True)
class StopInlineMessageLiveLocationRequest:
    """Parameters for stopping a live location inline message."""

    inline_message_id: InlineMessageID
    reply_markup: Optional[JSONSerialized[InlineKeyboardMarkup]] = None


@dataclass(frozen=True)
class SendVenueRequest:
    """Parameters for sending information about a venue."""

    chat_id: Union[ChatID, str]
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendContactRequest:
    """Parameters for sending a phone contact."""

    chat_id: Union[ChatID, str]
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    vcard: Optional[str] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendPollRequest:
    """Parameters for sending a native poll."""

    chat_id: Union[ChatID, str]
    question: str
    options: JSONSerialized[List[str]]
    is_anonymous: Optional[bool] = None
    type: Optional[PollType] = None
    allows_multiple_answers: Optional[bool] = None
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    explanation_parse_mode: Optional[ParseMode] = None
    open_period: Optional[int] = None
    close_date: Optional[int] = None
    is_closed: Optional[bool] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class StopPollRequest:
    """Parameters for stopping a poll sent by the bot."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    reply_markup: Optional[JSONSerialized[InlineKeyboardMarkup]] = None


@dataclass(frozen=True)
class SendDiceRequest:
    """Parameters for sending a Dice."""

    chat_id: Union[ChatID, str]
    emoji: Optional[DiceEmoji] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class SendChatActionRequest:
    """Parameters for sending a chat action."""

    chat_id: Union[ChatID, str]
    action: ChatAction


@dataclass(frozen=True)
class GetUserProfilePhotosRequest:
    """Parameters for getting a list of user profile pictures."""

    user_id: UserID
    offset: Optional[int] = None
    limit: Optional[int] = None


@dataclass(frozen=True)
class GetFileRequest:
    """Parameters for getting information to download a file."""

    file_id: FileID


@dataclass(frozen=True)
class KickChatMemberRequest:
    """Parameters for kicking a chat member."""

    chat_id: Union[ChatID, str]
    user_id: UserID
    until_date: Optional[int] = None


@dataclass(frozen=True)
class UnbanChatMemberRequest:
    """Parameters for unbanning a chat member."""

    chat_id: Union[ChatID, str]
    user_id: UserID


@dataclass(frozen=True)
class RestrictChatMemberRequest:
    """Parameters for restricting permissions of a chat member."""

    chat_id: Union[ChatID, str]
    user_id: UserID
    permissions: JSONSerialized[ChatPermissions]
    until_date: Optional[int] = None


@dataclass(frozen=True)
class PromoteChatMemberRequest:
    """Parameters for promoting a chat member to administrator."""

    chat_id: Union[ChatID, str]
    user_id: UserID
    can_change_info: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_promote_members: Optional[bool] = None


@dataclass(frozen=True)
class SetChatAdministratorCustomTitleRequest:
    """Parameters for setting an administrator's custom title."""

    chat_id: Union[ChatID, str]
    user_id: UserID
    custom_title: str


@dataclass(frozen=True)
class SetChatPermissionsRequest:
    """Parameters for setting the default chat permissions."""

    chat_id: Union[ChatID, str]
    permissions: JSONSerialized[ChatPermissions]


@dataclass(frozen=True)
class ExportChatInviteLinkRequest:
    """Parameters for exporting a chat's invite link."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class SetChatPhotoRequest:
    """Parameters for setting a chat's photo."""

    chat_id: Union[ChatID, str]
    photo: InputFile


@dataclass(frozen=True)
class DeleteChatPhotoRequest:
    """Parameters for deleting a chat's photo."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class SetChatTitleRequest:
    """Parameters for setting a chat's title."""

    chat_id: Union[ChatID, str]
    title: str


@dataclass(frozen=True)
class SetChatDescriptionRequest:
    """Parameters for setting a chat's description."""

    chat_id: Union[ChatID, str]
    description: str


@dataclass(frozen=True)
class PinChatMessageRequest:
    """Parameters for pinning a message in a chat."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    disable_notification: Optional[bool] = None


@dataclass(frozen=True)
class UnpinChatMessageRequest:
    """Parameters for unpinning the message from a chat."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class LeaveChatRequest:
    """Parameters for leaving a chat."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class GetChatRequest:
    """Parameters for getting information about a chat."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class GetChatAdministratorsRequest:
    """Parameters for getting the administrators of a chat."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class GetChatMembersCountRequest:
    """Parameters for getting the number of members in a chat."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class GetChatMemberRequest:
    """Parameters for getting information about a member in a chat."""

    chat_id: Union[ChatID, str]
    user_id: UserID


@dataclass(frozen=True)
class SetChatStickerSetRequest:
    """Parameters for setting the sticker set of a supergroup."""

    chat_id: Union[ChatID, str]
    sticker_set_name: str


@dataclass(frozen=True)
class DeleteChatStickerSetRequest:
    """Parameters for deleting the sticker set of a supergroup."""

    chat_id: Union[ChatID, str]


@dataclass(frozen=True)
class AnswerCallbackQueryRequest:
    """Parameters for answering a callback query from an inline keyboard."""

    callback_query_id: CallbackQueryID
    text: Optional[str] = None
    show_alert: Optional[bool] = None
    url: Optional[str] = None
    cache_time: Optional[int] = None


@dataclass(frozen=True)
class SetMyCommandsRequest:
    """Parameters for setting a bot's command list."""

    commands: JSONSerialized[List[BotCommand]]


@dataclass(frozen=True)
class EditMessageTextRequest:
    """Parameters for editing the text of a non-inline message."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    text: str
    parse_mode: Optional[ParseMode] = None
    disable_web_page_preview: Optional[bool] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditInlineMessageTextRequest:
    """Parameters for editing the text of an inline message."""

    inline_message_id: InlineMessageID
    text: str
    parse_mode: Optional[ParseMode] = None
    disable_web_page_preview: Optional[bool] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditMessageCaptionRequest:
    """Parameters for editing the caption of a non-inline message."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditInlineMessageCaptionRequest:
    """Parameters for editing the caption of an inline message."""

    inline_message_id: InlineMessageID
    caption: Optional[str] = None
    parse_mode: Optional[ParseMode] = None
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditMessageMediaRequest:
    """Parameters for editing the media of a non-inline message."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    media: JSONSerialized[InputMedia]
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditInlineMessageMediaRequest:
    """Parameters for editing the media of an inline message."""

    inline_message_id: InlineMessageID
    media: JSONSerialized[InputMedia]
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditMessageReplyMarkupRequest:
    """Parameters for editing the reply markup of a non-inline message."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class EditInlineMessageReplyMarkupRequest:
    """Parameters for editing the reply markup of an inline message."""

    inline_message_id: InlineMessageID
    reply_markup: Optional[JSONSerialized[ReplyMarkup]] = None


@dataclass(frozen=True)
class DeleteMessageRequest:
    """Parameters for deleting a message."""

    chat_id: Union[ChatID, str]
    message_id: MessageID
