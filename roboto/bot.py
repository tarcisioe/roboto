"""The main bot class for Roboto."""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Optional, Union

from .api_types import (
    BotUser,
    ChatID,
    InlineKeyboardMarkup,
    InlineMessageID,
    InputFile,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    MessageID,
    ParseMode,
    ReplyMarkup,
    Token,
    Update,
)
from .asks import Session
from .datautil import from_json
from .http_api import (
    HTTPMethod,
    make_multipart_request,
    make_multipart_request_with_attachments,
    make_request,
)
from .media import extract_medias
from .request_types import (
    EditInlineMessageLiveLocationRequest,
    EditMessageLiveLocationRequest,
    ForwardMessageRequest,
    GetUpdatesRequest,
    SendAnimationRequest,
    SendAudioRequest,
    SendDocumentRequest,
    SendLocationRequest,
    SendMediaGroupRequest,
    SendMessageRequest,
    SendPhotoRequest,
    SendVideoNoteRequest,
    SendVideoRequest,
    SendVoiceRequest,
    StopInlineMessageLiveLocationRequest,
    StopMessageLiveLocationRequest,
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
        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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

        return from_json(
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
            chat_id: The ID of the chat to send a video note to.
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

        return from_json(
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

        return from_json(
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
        """editMessageLiveLocation API method (for normal messages).

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

        return from_json(
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

        Even though the REST API method for normal messages is the same, for a
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

        return from_json(
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
        """stopMessageLiveLocation API method (for normal messages).

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

        return from_json(
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

        Even though the REST API method for normal messages is the same, for a
        less error-prone API this is split into two methods. See
        `stop_message_live_location`.

        Args:
            inline_message_id: The id of the inline message to stop.
            reply_markup: Markup for a new inline keyboard.
        """

        request = StopInlineMessageLiveLocationRequest(
            inline_message_id, maybe_json_serialize(reply_markup),
        )

        return from_json(
            Message,
            await make_request(
                self.session, HTTPMethod.POST, '/stopMessageLiveLocation', request
            ),
        )


__all__ = [
    'BotAPI',
]
