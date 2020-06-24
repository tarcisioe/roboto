"""The main bot class for Roboto."""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Optional, Union

from asks import Session

from .api_types import (
    BotCommand,
    BotUser,
    CallbackQueryID,
    Chat,
    ChatAction,
    ChatID,
    ChatMember,
    ChatPermissions,
    DiceEmoji,
    File,
    FileID,
    InlineKeyboardMarkup,
    InlineMessageID,
    InputFile,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    MessageID,
    ParseMode,
    Poll,
    PollType,
    ReplyMarkup,
    Token,
    Update,
    UserID,
    UserProfilePhotos,
)
from .datautil import from_json_like
from .http_api import (
    HTTPMethod,
    make_multipart_request,
    make_multipart_request_with_attachments,
    make_request,
)
from .media import extract_medias
from .request_types import (
    AnswerCallbackQueryRequest,
    DeleteChatPhotoRequest,
    DeleteChatStickerSetRequest,
    DeleteMessageRequest,
    EditInlineMessageCaptionRequest,
    EditInlineMessageLiveLocationRequest,
    EditInlineMessageMediaRequest,
    EditInlineMessageReplyMarkupRequest,
    EditInlineMessageTextRequest,
    EditMessageCaptionRequest,
    EditMessageLiveLocationRequest,
    EditMessageMediaRequest,
    EditMessageReplyMarkupRequest,
    EditMessageTextRequest,
    ExportChatInviteLinkRequest,
    ForwardMessageRequest,
    GetChatAdministratorsRequest,
    GetChatMemberRequest,
    GetChatMembersCountRequest,
    GetChatRequest,
    GetFileRequest,
    GetUpdatesRequest,
    GetUserProfilePhotosRequest,
    KickChatMemberRequest,
    LeaveChatRequest,
    PinChatMessageRequest,
    PromoteChatMemberRequest,
    RestrictChatMemberRequest,
    SendAnimationRequest,
    SendAudioRequest,
    SendChatActionRequest,
    SendContactRequest,
    SendDiceRequest,
    SendDocumentRequest,
    SendLocationRequest,
    SendMediaGroupRequest,
    SendMessageRequest,
    SendPhotoRequest,
    SendPollRequest,
    SendVenueRequest,
    SendVideoNoteRequest,
    SendVideoRequest,
    SendVoiceRequest,
    SetChatAdministratorCustomTitleRequest,
    SetChatDescriptionRequest,
    SetChatPermissionsRequest,
    SetChatPhotoRequest,
    SetChatStickerSetRequest,
    SetChatTitleRequest,
    SetMyCommandsRequest,
    StopInlineMessageLiveLocationRequest,
    StopMessageLiveLocationRequest,
    StopPollRequest,
    UnbanChatMemberRequest,
    UnpinChatMessageRequest,
    json_serialize,
    maybe_json_serialize,
)
from .url import URL

TELEGRAM_BOT_API_URL = URL.make('https://api.telegram.org')


@dataclass
class BotAPI:
    """Bot API wrapper.

    Avoid creating objects from this class directly through its constructor.
    Use the static method `make` which does everything for you (and its API
    is independent from the HTTP library).

    Args:
        token: The Telegram API token for the bot.
        session: An asks.Session object.
    """

    session: Session

    @staticmethod
    @asynccontextmanager
    async def make(
        token: Token, api_url: URL = TELEGRAM_BOT_API_URL,
    ):
        """Context manager for creating a BotAPI object.

        This is the preferred method to create a BotAPI object.

        Args:
            token: The Telegram Bot API token for the bot.
            api_url: The Telegram Bot API URL. Just for future-proofing. The
                     default should be ok.

        Yields:
            A BotAPI object.
        """
        async with Session(base_location=api_url, endpoint=f'/bot{token}') as s:
            yield BotAPI(s)

    async def get_me(self) -> BotUser:
        """getMe API method.

        Returns:
            User: the user object representing the bot itself.
        """
        return from_json_like(
            BotUser, await make_request(self.session, HTTPMethod.GET, '/getMe')
        )

    async def get_updates(
        self,
        offset: int = None,
        limit: int = None,
        timeout: int = None,
        allowed_updates: List[str] = None,
    ) -> List[Update]:
        """getUpdates API method. Won't work if a webhook is setup.

        Args:
            offset: The offset to begin in the updates list.
            limit: How many updates to get at maximum.
            timeout: How long to long poll for.
            allowed_updates: Which kind of updates to fetch.

        Returns:
            A list of Update objects.
        """
        request = GetUpdatesRequest(offset, limit, timeout, allowed_updates)

        return from_json_like(
            List[Update],
            await make_request(self.session, HTTPMethod.GET, '/getUpdates', request),
        )

    async def send_message(
        self,
        chat_id: Union[ChatID, str],
        text: str,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendMessage API method.

        Args:
            chat_id: The ID of the chat to send a message to.
            text: The message text.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            disable_web_page_preview: Avoid showing previews for links.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for offering an interface for the user to
                          reply to the bot.

        Returns:
            The Message object for the message that was sent.
        """
        request = SendMessageRequest(
            chat_id,
            text,
            parse_mode,
            disable_web_page_preview,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(self.session, HTTPMethod.POST, '/sendMessage', request),
        )

    async def forward_message(
        self,
        chat_id: Union[ChatID, str],
        from_chat_id: Union[ChatID, str],
        message_id: MessageID,
        *,
        disable_notification: Optional[bool] = None,
    ) -> Message:
        """forwardMessage API method.

        Args:
            chat_id: The ID of the chat to forward the message to.
            from_chat_id: The ID of the chat where the message is coming from.
            message_id: The ID of the message to forward.
            disable_notification: Do not notify users that the message was sent.

        Returns:
            The Message object for the message that was forwarded.
        """
        request = ForwardMessageRequest(
            chat_id, from_chat_id, message_id, disable_notification,
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/forwardMessage', request
            ),
        )

    async def send_photo(
        self,
        chat_id: Union[ChatID, str],
        photo: InputFile,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendPhoto API method.

        Args:
            chat_id: The ID of the chat to send a photo to.
            photo: The path of the image file to send.
            caption: A caption to add to the image.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.

        Returns:
            The Message object for the message that was sent.
        """

        request = SendPhotoRequest(
            chat_id,
            photo,
            caption,
            parse_mode,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message, await make_multipart_request(self.session, '/sendPhoto', request),
        )

    async def send_audio(
        self,
        chat_id: Union[ChatID, str],
        audio: InputFile,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        thumb: Optional[InputFile] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendAudio API method.

        Args:
            chat_id: The ID of the chat to send an audio to.
            audio: An InputFile to use to send the audio.
                   See the documentation on InputFile.
            caption: A caption to add to the audio.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            duration: The audio duration.
            performer: The audio performer.
            title: The audio title.
            thumb: An InputFile for the thumbnail to be used for the audio.
                   See the documentation on InputFile.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.

        Returns:
            The Message object for the message that was sent.
        """

        request = SendAudioRequest(
            chat_id,
            audio,
            caption,
            parse_mode,
            duration,
            performer,
            title,
            thumb,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message, await make_multipart_request(self.session, '/sendAudio', request),
        )

    async def send_document(
        self,
        chat_id: Union[ChatID, str],
        document: InputFile,
        thumb: Optional[InputFile] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendDocument API method.

        Args:
            chat_id: The ID of the chat to send a document to.
            document: An InputFile to use to send the document.
                      See the documentation on InputFile.
            thumb: An InputFile for the thumbnail to be used for the document.
                   See the documentation on InputFile.
            caption: A caption to add to the document.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.

        Returns:
            The Message object for the message that was sent.
        """

        request = SendDocumentRequest(
            chat_id,
            document,
            thumb,
            caption,
            parse_mode,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_multipart_request(self.session, '/sendDocument', request),
        )

    async def send_video(
        self,
        chat_id: Union[ChatID, str],
        video: InputFile,
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        thumb: Optional[InputFile] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        supports_streaming: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendVideo API method.

        Args:
            chat_id: The ID of the chat to send a video to.
            video: An InputFile to use to send the video.
                   See the documentation on InputFile.
            duration: The video duration.
            width: The video width.
            height: The video height.
            thumb: An InputFile for the thumbnail to be used for the video.
                   See the documentation on InputFile.
            caption: A caption to add to the video.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            supports_streaming: Should be True if the video supports streaming.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.

        Returns:
            The Message object for the message that was sent.
        """

        request = SendVideoRequest(
            chat_id,
            video,
            duration,
            width,
            height,
            thumb,
            caption,
            parse_mode,
            disable_notification,
            supports_streaming,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message, await make_multipart_request(self.session, '/sendVideo', request),
        )

    async def send_animation(
        self,
        chat_id: Union[ChatID, str],
        animation: InputFile,
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        thumb: Optional[InputFile] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendAnimation API method.

        Args:
            chat_id: The ID of the chat to send an animation to.
            animation: An InputFile to use to send the animation.
                       See the documentation on InputFile.
            duration: The animation duration.
            width: The animation width.
            height: The animation height.
            thumb: An InputFile for the thumbnail to be used for the animation.
                   See the documentation on InputFile.
            caption: A caption to add to the animation.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.

        Returns:
            The Message object for the message that was sent.
        """

        request = SendAnimationRequest(
            chat_id,
            animation,
            duration,
            width,
            height,
            thumb,
            caption,
            parse_mode,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_multipart_request(self.session, '/sendAnimation', request),
        )

    async def send_voice(
        self,
        chat_id: Union[ChatID, str],
        voice: InputFile,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        duration: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendVoice API method.

        Args:
            chat_id: The ID of the chat to send a voice note to.
            voice: An InputFile to use to send the voice note.
                   See the documentation on InputFile. Must be an OGG audio file
                   encoded with OPUS.
            caption: A caption to add to the voice note.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            duration: The voice note duration.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.

        Returns:
            The Message object for the message that was sent.
        """

        request = SendVoiceRequest(
            chat_id,
            voice,
            caption,
            parse_mode,
            duration,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message, await make_multipart_request(self.session, '/sendVoice', request),
        )

    async def send_video_note(
        self,
        chat_id: Union[ChatID, str],
        video_note: InputFile,
        duration: Optional[int] = None,
        length: Optional[int] = None,
        thumb: Optional[InputFile] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendVideoNote API method.

        Args:
            chat_id: The ID of the chat to send a video note to.
            video_note: An InputFile to use to send the video note.
                        See the documentation on InputFile. Must be a square mp4 video.
            duration: The video note duration.
            length: The video note length (diameter).
            thumb: An InputFile for the thumbnail to be used for the animation.
                   See the documentation on InputFile.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.

        Returns:
            The Message object for the message that was sent.
        """

        request = SendVideoNoteRequest(
            chat_id,
            video_note,
            duration,
            length,
            thumb,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_multipart_request(self.session, '/sendVideoNote', request),
        )

    async def send_media_group(
        self,
        chat_id: Union[ChatID, str],
        media: List[Union[InputMediaPhoto, InputMediaVideo]],
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
    ) -> List[Message]:
        """sendMediaGroup API method.

        Args:
            chat_id: The ID of the chat to send a media group to.
            media: An array of InputMediaPhoto and InputMediaVideo to send as a
                   media group.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
        """

        media, attachments = extract_medias(media)

        request = SendMediaGroupRequest(
            chat_id, json_serialize(media), disable_notification, reply_to_message_id,
        )

        return from_json_like(
            List[Message],
            await make_multipart_request_with_attachments(
                self.session, '/sendMediaGroup', request, attachments
            ),
        )

    async def send_location(
        self,
        chat_id: Union[ChatID, str],
        latitude: float,
        longitude: float,
        live_period: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendLocation API method.

        Args:
            chat_id: The ID of the chat to send a location or live location to.
            latitude: Latitude of the location.
            longitude: Longitude of the location.
            live_period: Period in seconds for which the location will be updated.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.
        """

        request = SendLocationRequest(
            chat_id,
            latitude,
            longitude,
            live_period,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(self.session, HTTPMethod.POST, '/sendLocation', request),
        )

    async def edit_message_live_location(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        latitude: float,
        longitude: float,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageLiveLocation API method (for non-inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_inline_message_live_location`.

        Args:
            chat_id: The ID of the chat where the message to be edited is.
            message_id: The id of the message to edit.
            latitude: The new latitude for editing the location.
            longitude: The new longitude for editing the location.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditMessageLiveLocationRequest(
            chat_id,
            message_id,
            latitude,
            longitude,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageLiveLocation', request
            ),
        )

    async def edit_inline_message_live_location(
        self,
        inline_message_id: InlineMessageID,
        latitude: float,
        longitude: float,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageLiveLocation API method (for inline messages).

        Even though the REST API method for non-inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_message_live_location`.

        Args:
            inline_message_id: The id of the inline message to edit.
            latitude: The new latitude for editing the location.
            longitude: The new longitude for editing the location.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditInlineMessageLiveLocationRequest(
            inline_message_id, latitude, longitude, maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageLiveLocation', request
            ),
        )

    async def stop_message_live_location(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """stopMessageLiveLocation API method (for non-inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `stop_inline_message_live_location`.

        Args:
            chat_id: The ID of the chat where the message to be stopped is.
            message_id: The id of the message to stop.
            reply_markup: Markup for a new inline keyboard.
        """

        request = StopMessageLiveLocationRequest(
            chat_id, message_id, maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/stopMessageLiveLocation', request
            ),
        )

    async def stop_inline_message_live_location(
        self,
        inline_message_id: InlineMessageID,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """stopMessageLiveLocation API method (for inline messages).

        Even though the REST API method for non-inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `stop_message_live_location`.

        Args:
            inline_message_id: The id of the inline message to stop.
            reply_markup: Markup for a new inline keyboard.
        """

        request = StopInlineMessageLiveLocationRequest(
            inline_message_id, maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/stopMessageLiveLocation', request
            ),
        )

    async def send_venue(
        self,
        chat_id: Union[ChatID, str],
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: Optional[str] = None,
        foursquare_type: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendVenue API method.

        Args:
            chat_id: The ID of the chat to send a venue to.
            latitude: Latitude of the venue.
            longitude: Longitude of the venue.
            title: Name of the venue.
            address: Address of the venue.
            foursquare_id: Foursquare identifier of the venue.
            foursquare_type: Foursquare type of the venue, if known.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.
        """

        request = SendVenueRequest(
            chat_id,
            latitude,
            longitude,
            title,
            address,
            foursquare_id,
            foursquare_type,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(self.session, HTTPMethod.POST, '/sendVenue', request),
        )

    async def send_contact(
        self,
        chat_id: Union[ChatID, str],
        phone_number: str,
        first_name: str,
        last_name: Optional[str],
        vcard: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendContact API method.

        Args:
            chat_id: The ID of the chat to send a phone contact to.
            phone_number: The contact's phone number.
            first_name: The contacts's first name.
            last_name: The contacts's last name.
            vcard: Additional data about the contact in the format of a vCard.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.
        """

        request = SendContactRequest(
            chat_id,
            phone_number,
            first_name,
            last_name,
            vcard,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(self.session, HTTPMethod.POST, '/sendContact', request),
        )

    async def send_poll(
        self,
        chat_id: Union[ChatID, str],
        question: str,
        options: List[str],
        is_anonymous: Optional[bool] = None,
        poll_type: Optional[PollType] = None,
        allows_multiple_answers: Optional[bool] = None,
        correct_option_id: Optional[int] = None,
        explanation: Optional[str] = None,
        explanation_parse_mode: Optional[ParseMode] = None,
        open_period: Optional[int] = None,
        close_date: Optional[int] = None,
        is_closed: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendPoll API method.

        Args:
            chat_id: The ID of the chat to send a phone contact to.
            question: The poll question.
            options: A list of answer options.
            is_anonymous: Whether the poll should be anonymous. Default is anonymous.
            poll_type: Either "quiz" to create a quiz or "regular" for a regular poll.
            allows_multiple_answers: Whether the poll allows multiple answers by the
                                     same user.
            correct_option_id: (0-based) index of the correct answer if this is a quiz.
            explanation: Text to show if the user chooses an incorrect answer or taps
                         the lamp icon on a quiz.
            explanation_parse_mode: How to parse the text in the explanation (see
                                    `ParseMode`). Parses as plain text if omitted.
            open_period: Amout of time (in seconds) the poll will be active  after
                         creation. Can't be used together with `close_date`.
            close_date: Point in time (Unix timestamp) when the poll will be
                        automatically closed. Can't be used together with `open_period`.
            is_closed: Whether to automatically close the poll. Useful for previewing a
                       poll.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.
        """

        request = SendPollRequest(
            chat_id,
            question,
            json_serialize(options),
            is_anonymous,
            poll_type,
            allows_multiple_answers,
            correct_option_id,
            explanation,
            explanation_parse_mode,
            open_period,
            close_date,
            is_closed,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(self.session, HTTPMethod.POST, '/sendPoll', request),
        )

    async def stop_poll(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Poll:
        """stopPoll API method.

        Args:
            chat_id: The ID of the chat where the poll to be stopped is.
            message_id: The id of the message with the poll to stop.
            reply_markup: Markup for a new inline keyboard.
        """

        request = StopPollRequest(
            chat_id, message_id, maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Poll,
            await make_request(self.session, HTTPMethod.POST, '/stopPoll', request),
        )

    async def send_dice(
        self,
        chat_id: Union[ChatID, str],
        emoji: Optional[DiceEmoji] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """sendDice API method.

        Args:
            chat_id: The ID of the chat to send a phone contact to.
            emoji: The emoji to use in the Dice message. See `DiceEmoji`.
            disable_notification: Do not notify users that the message was sent.
            reply_to_message_id: ID of a message that the sent message should
                                 be a reply to.
            reply_markup: Markup for additional interface options for replying.
        """

        request = SendDiceRequest(
            chat_id,
            emoji,
            disable_notification,
            reply_to_message_id,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(self.session, HTTPMethod.POST, '/sendDice', request),
        )

    async def send_chat_action(
        self, chat_id: Union[ChatID, str], action: ChatAction,
    ) -> bool:
        """sendChatAction API method.

        Args:
            chat_id: The ID of the chat to send the chat action to.
            action: The action to show to the user.
        """

        request = SendChatActionRequest(chat_id, action)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/sendChatAction', request
            ),
        )

    async def get_user_profile_photos(
        self,
        user_id: UserID,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> UserProfilePhotos:
        """getUserProfilePhotos API method.

        Args:
            user_id: The ID of the user to get the profile photos.
            offset: Sequential number of the first photo to be returned.
                    By default, all photos are returned.
            limit: Limits the number of photos to be retrieved. Defaults to 100.
        """

        request = GetUserProfilePhotosRequest(user_id, offset, limit)

        return from_json_like(
            UserProfilePhotos,
            await make_request(
                self.session, HTTPMethod.POST, '/getUserProfilePhotos', request
            ),
        )

    async def get_file(self, file_id: FileID) -> File:
        """getFile API method.

        Args:
            file_id: The ID of the file information to fetch.
        """

        request = GetFileRequest(file_id)

        return from_json_like(
            File,
            await make_request(self.session, HTTPMethod.POST, '/getFile', request),
        )

    async def kick_chat_member(
        self,
        chat_id: Union[ChatID, str],
        user_id: UserID,
        until_date: Optional[int] = None,
    ) -> bool:
        """kickChatMember API method.

        Args:
            chat_id: The ID of the group or channel from where to remove the user.
            user_id: The ID of the user to kick.
            until_date: Date when the user will be unbanned, Unix time.
                        Must be from 30 seconds to 366 days from the current time.
                        If outside of these bounds, the user is considered to be banned
                        forever.
        """

        request = KickChatMemberRequest(chat_id, user_id, until_date)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/kickChatMember', request,
            ),
        )

    async def unban_chat_member(
        self, chat_id: Union[ChatID, str], user_id: UserID,
    ) -> bool:
        """unbanChatMember API method.

        Args:
            chat_id: The ID of the group or channel from where to unban the user.
            user_id: The ID of the user to unban.
        """

        request = UnbanChatMemberRequest(chat_id, user_id)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/unbanChatMember', request,
            ),
        )

    async def restrict_chat_member(
        self,
        chat_id: Union[ChatID, str],
        user_id: UserID,
        permissions: ChatPermissions,
        until_date: Optional[int] = None,
    ) -> bool:
        """restrictChatMember API method.

        Args:
            chat_id: The ID of the group or channel where the user should be restricted.
            user_id: The ID of the user to restrict.
            permissions: The new user permissions. Pass False to a permission to
                         restrict it, or True to a permission to lift a restriction.
            until_date: Date when the user will have the restrictions lifted, Unix time.
                        Must be from 30 seconds to 366 days from the current time.
                        If outside of these bounds, the user is considered to be banned
                        forever.
        """

        request = RestrictChatMemberRequest(
            chat_id, user_id, json_serialize(permissions), until_date,
        )

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/restrictChatMember', request,
            ),
        )

    async def promote_chat_member(
        self,
        chat_id: Union[ChatID, str],
        user_id: UserID,
        can_change_info: Optional[bool] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_promote_members: Optional[bool] = None,
    ) -> bool:
        """promoteChatMember API method.

        If all permissions are `False`, the user is demoted.

        Args:
            chat_id: The ID of the group or channel where the user should be promoted to
                     administrator.
            user_id: The ID of the user to promote to administrator.
            can_change_info: Whether the user should change chat title, photo and other
                             settings.
            can_post_messages: Whether the user should create channel posts, channels
                               only.
            can_edit_messages: Whether the user should edit messages of other users and
                               can pin messages, channels only.
            can_delete_messages: Whether the user should delete messages of other users.
            can_invite_users: Whether the user should invite new users to the chat.
            can_restrict_members: Whether the user should restrict, ban or unban chat
                                  members.
            can_pin_messages: Whether the user should pin messages, supergroups only.
            can_promote_members: Whether the user should add new administrators with a
                                 subset of their own privileges or demote administrators
                                 that he has promoted, directly or indirectly (promoted
                                 by administrators that were appointed by him).

        """

        request = PromoteChatMemberRequest(
            chat_id,
            user_id,
            can_change_info,
            can_post_messages,
            can_edit_messages,
            can_delete_messages,
            can_invite_users,
            can_restrict_members,
            can_pin_messages,
            can_promote_members,
        )

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/promoteChatMember', request,
            ),
        )

    async def set_chat_administrator_custom_title(
        self, chat_id: Union[ChatID, str], user_id: UserID, custom_title: str,
    ) -> bool:
        """setChatAdministratorCustomTitle API method.

        Args:
            chat_id: The ID of the group or channel where the administrator is.
            user_id: The ID of the administration whose custom title shoulde be set.
            custom_title: New custom title for the administrator.
        """

        request = SetChatAdministratorCustomTitleRequest(chat_id, user_id, custom_title)

        return from_json_like(
            bool,
            await make_request(
                self.session,
                HTTPMethod.POST,
                '/setChatAdministratorCustomTitle',
                request,
            ),
        )

    async def set_chat_permissions(
        self, chat_id: Union[ChatID, str], permissions: ChatPermissions,
    ) -> bool:
        """setChatPermissions API method.

        Args:
            chat_id: The ID of the group or channel where the user should be restricted.
            permissions: The new user permissions. Pass False to a permission to
                         restrict it, or True to a permission to lift a restriction.
        """

        request = SetChatPermissionsRequest(chat_id, json_serialize(permissions))

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/setChatPermissions', request,
            ),
        )

    async def export_chat_invite_link(self, chat_id: Union[ChatID, str]) -> str:
        """exportChatInviteLink API method.

        Args:
            chat_id: The ID of the group or channel to get the invite link to.
        """

        request = ExportChatInviteLinkRequest(chat_id)

        return from_json_like(
            str,
            await make_request(
                self.session, HTTPMethod.POST, '/exportChatInviteLink', request,
            ),
        )

    async def set_chat_photo(
        self, chat_id: Union[ChatID, str], photo: InputFile,
    ) -> bool:
        """setChatPhoto API method.

        Args:
            chat_id: The ID of the group or channel to change the photo of.
            photo: The photo to use as an `InputFile`.
        """

        request = SetChatPhotoRequest(chat_id, photo)

        return from_json_like(
            bool, await make_multipart_request(self.session, '/setChatPhoto', request),
        )

    async def delete_chat_photo(self, chat_id: Union[ChatID, str]) -> bool:
        """deleteChatPhoto API method.

        Args:
            chat_id: The ID of the group or channel to delete the photo of.
        """

        request = DeleteChatPhotoRequest(chat_id)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/deleteChatPhoto', request
            ),
        )

    async def set_chat_title(self, chat_id: Union[ChatID, str], title: str) -> bool:
        """setChatTitle API method.

        Args:
            chat_id: The ID of the group or channel to set the title of.
            title: The new chat title.
        """

        request = SetChatTitleRequest(chat_id, title)

        return from_json_like(
            bool,
            await make_request(self.session, HTTPMethod.POST, '/setChatTitle', request),
        )

    async def set_chat_description(
        self, chat_id: Union[ChatID, str], description: str,
    ) -> bool:
        """setChatDescription API method.

        Args:
            chat_id: The ID of the group or channel to set the description of.
            description: The new chat description.
        """

        request = SetChatDescriptionRequest(chat_id, description)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/setChatDescription', request,
            ),
        )

    async def pin_chat_message(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        disable_notification: Optional[bool] = None,
    ) -> bool:
        """pinChatMessage API method.

        Args:
            chat_id: The ID of the group or channel where to pin the message.
            message_id: The ID of the message to pin.
            disable_notification: Do not notify users that the message was pinned.
        """

        request = PinChatMessageRequest(chat_id, message_id, disable_notification)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/pinChatMessage', request,
            ),
        )

    async def unpin_chat_message(self, chat_id: Union[ChatID, str]) -> bool:
        """unpinChatMessage API method.

        Args:
            chat_id: The ID of the group or channel to unpin the pinned message from.
        """

        request = UnpinChatMessageRequest(chat_id)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/unpinChatMessage', request,
            ),
        )

    async def leave_chat(self, chat_id: Union[ChatID, str]) -> bool:
        """leaveChat API method.

        Args:
            chat_id: The ID of the group or channel to leave.
        """

        request = LeaveChatRequest(chat_id)

        return from_json_like(
            bool,
            await make_request(self.session, HTTPMethod.POST, '/leaveChat', request),
        )

    async def get_chat(self, chat_id: Union[ChatID, str]) -> Chat:
        """getChat API method.

        Args:
            chat_id: The ID of the chat to get information about.
        """

        request = GetChatRequest(chat_id)

        return from_json_like(
            Chat,
            await make_request(self.session, HTTPMethod.POST, '/getChat', request),
        )

    async def get_chat_administrators(
        self, chat_id: Union[ChatID, str],
    ) -> List[ChatMember]:
        """getChatAdministrators API method.

        Args:
            chat_id: The ID of the group or channel to get the the administrators of.
        """

        request = GetChatAdministratorsRequest(chat_id)

        return from_json_like(
            List[ChatMember],
            await make_request(
                self.session, HTTPMethod.POST, '/getChatAdministrators', request,
            ),
        )

    async def get_chat_members_count(self, chat_id: Union[ChatID, str]) -> int:
        """getChatMembersCount API method.

        Args:
            chat_id: The ID of the group or channel to get the number of members of.
        """

        request = GetChatMembersCountRequest(chat_id)

        return from_json_like(
            int,
            await make_request(
                self.session, HTTPMethod.POST, '/getChatMembersCount', request,
            ),
        )

    async def get_chat_member(
        self, chat_id: Union[ChatID, str], user_id: UserID,
    ) -> ChatMember:
        """getChatMember API method.

        Args:
            chat_id: The ID of the group or channel to get information on the member.
            user_id: The ID of the user to get information about.
        """

        request = GetChatMemberRequest(chat_id, user_id)

        return from_json_like(
            ChatMember,
            await make_request(
                self.session, HTTPMethod.POST, '/getChatMember', request,
            ),
        )

    async def set_chat_sticker_set(
        self, chat_id: Union[ChatID, str], sticker_set_name: str,
    ) -> bool:
        """setChatStickerSet API method.

        Args:
            chat_id: The ID of the group to set the sticker set of.
            sticker_set_name: The name of the sticker set to be set as the group sticker
                              set.
        """

        request = SetChatStickerSetRequest(chat_id, sticker_set_name)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/setChatStickerSet', request,
            ),
        )

    async def delete_chat_sticker_set(self, chat_id: Union[ChatID, str]) -> bool:
        """deleteChatStickerSet API method.

        Args:
            chat_id: The ID of the group to delete the sticker set of.
        """

        request = DeleteChatStickerSetRequest(chat_id)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/deleteChatStickerSet', request,
            ),
        )

    async def answer_callback_query(
        self,
        callback_query_id: CallbackQueryID,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> bool:
        """answerCallbackQuery API method.

        Args:
            callback_query_id: The id of the callback query to reply to.
            text: The text to show the user in the notification.
            show_alert: Use an alert instead of a notification on top of the chat
                        screen.
            url: URL for the user's client to open. If the button that generated the
                 query was a `callback_game` button, this may be a link to a Game.
            cache_time: The maximum amount of time the client may cache the result of
                        the callback query.
        """

        request = AnswerCallbackQueryRequest(
            callback_query_id, text, show_alert, url, cache_time,
        )

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/answerCallbackQuery', request,
            ),
        )

    async def set_my_commands(self, commands: List[BotCommand]) -> bool:
        """setMyCommands API method.

        Args:
            commands: List of BotCommand objects describing the bot's commands.
        """

        request = SetMyCommandsRequest(json_serialize(commands))

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/setMyCommands', request,
            ),
        )

    async def get_my_commands(self) -> List[BotCommand]:
        """getMyCommands API method."""

        return from_json_like(
            List[BotCommand],
            await make_request(self.session, HTTPMethod.POST, '/getMyCommands'),
        )

    async def edit_message_text(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        text: str,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageText API method (for non-inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_inline_message_text`.

        Args:
            chat_id: The ID of the chat where the message to be edited is.
            message_id: The id of the message to edit.
            text: New text for the edited message.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            disable_web_page_preview: Avoid showing previews for links.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditMessageTextRequest(
            chat_id,
            message_id,
            text,
            parse_mode,
            disable_web_page_preview,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageText', request
            ),
        )

    async def edit_inline_message_text(
        self,
        inline_message_id: InlineMessageID,
        text: str,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageText API method (for inline messages).

        Even though the REST API method for non-inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_message_text`.

        Args:
            inline_message_id: The id of the inline message to edit.
            text: New text for the edited message.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            disable_web_page_preview: Avoid showing previews for links.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditInlineMessageTextRequest(
            inline_message_id,
            text,
            parse_mode,
            disable_web_page_preview,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageText', request
            ),
        )

    async def edit_message_caption(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageCaption API method (for non-inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_inline_message_caption`.

        Args:
            chat_id: The ID of the chat where the message to be edited is.
            message_id: The id of the message to edit.
            caption: New caption for the edited message. Can be omitted for removing the
                     caption.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditMessageCaptionRequest(
            chat_id,
            message_id,
            caption,
            parse_mode,
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageCaption', request
            ),
        )

    async def edit_inline_message_caption(
        self,
        inline_message_id: InlineMessageID,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageCaption API method (for inline messages).

        Even though the REST API method for normal messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_message_caption`.

        Args:
            inline_message_id: The id of the inline message to edit.
            caption: New caption for the edited message. Can be omitted for removing the
                     caption.
            parse_mode: How to parse the text (see `ParseMode`). Parses as
                        plain text if omitted.
            disable_web_page_preview: Avoid showing previews for links.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditInlineMessageCaptionRequest(
            inline_message_id, caption, parse_mode, maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageCaption', request
            ),
        )

    async def edit_message_media(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        media: InputMedia,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageMedia API method (for non-inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_inline_message_media`.

        Args:
            chat_id: The ID of the chat where the message to be edited is.
            message_id: The id of the message to edit.
            media: The new media for the message.
            reply_markup: Markup for a new inline keyboard.
        """

        [media], attachments = extract_medias([media])

        request = EditMessageMediaRequest(
            chat_id,
            message_id,
            json_serialize(media),
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_multipart_request_with_attachments(
                self.session, '/editMessageMedia', request, attachments,
            ),
        )

    async def edit_inline_message_media(
        self,
        inline_message_id: InlineMessageID,
        media: InputMedia,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageMedia API method (for inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_message_media`.

        Args:
            inline_message_id: The id of the inline message to edit.
            media: The new media for the message.
            reply_markup: Markup for a new inline keyboard.
        """

        [media], attachments = extract_medias([media])

        request = EditInlineMessageMediaRequest(
            inline_message_id,
            json_serialize(media),
            maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_multipart_request_with_attachments(
                self.session, '/editMessageMedia', request, attachments,
            ),
        )

    async def edit_message_reply_markup(
        self,
        chat_id: Union[ChatID, str],
        message_id: MessageID,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageReplyMarkup API method (for non-inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_inline_message_reply_markup`.

        Args:
            chat_id: The ID of the chat where the message to be edited is.
            message_id: The id of the message to edit.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditMessageReplyMarkupRequest(
            chat_id, message_id, maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageReplyMarkup', request,
            ),
        )

    async def edit_inline_message_reply_markup(
        self,
        inline_message_id: InlineMessageID,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """editMessageReplyMarkup API method (for inline messages).

        Even though the REST API method for inline messages is the same, for a
        less error-prone API this is split into two methods. See
        `edit_message_reply_markup`.

        Args:
            inline_message_id: The id of the inline message to edit.
            reply_markup: Markup for a new inline keyboard.
        """

        request = EditInlineMessageReplyMarkupRequest(
            inline_message_id, maybe_json_serialize(reply_markup),
        )

        return from_json_like(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/editMessageReplyMarkup', request,
            ),
        )

    async def delete_message(
        self, chat_id: Union[ChatID, str], message_id: MessageID,
    ) -> bool:
        """deleteMessage API method.

        Args:
            chat_id: The ID of the chat to delete the message.
            message_id: The ID of the message to delete.
        """

        request = DeleteMessageRequest(chat_id, message_id)

        return from_json_like(
            bool,
            await make_request(
                self.session, HTTPMethod.POST, '/deleteMessage', request,
            ),
        )


__all__ = [
    'BotAPI',
]
