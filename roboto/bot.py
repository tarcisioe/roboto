"""The main bot class for Roboto."""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Optional, Union

from .api_types import (
    BotUser,
    ChatID,
    Message,
    MessageID,
    ParseMode,
    ReplyMarkup,
    Token,
    Update,
)
from .asks import Session
from .datautil import from_json
from .http_api import HTTPMethod, make_multipart_request, make_request
from .request_types import (
    ForwardMessageRequest,
    GetUpdatesRequest,
    InputFile,
    SendMessageRequest,
    SendPhotoRequest,
    json_serialize,
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
            json_serialize(reply_markup),
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
            chat_id: The ID of the chat to send a message to.
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
            json_serialize(reply_markup),
        )

        return from_json(
            Message, await make_multipart_request(self.session, '/sendPhoto', request),
        )


__all__ = [
    'BotAPI',
]
