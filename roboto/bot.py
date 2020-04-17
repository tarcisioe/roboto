"""The main bot class for Roboto."""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Optional, Union

from asks import Session

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
from .datautil import from_json
from .http_api import HTTPMethod, make_request
from .request_types import GetUpdatesRequest, SendMessageRequest
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
            reply_markup,
        )

        return from_json(
            Message,
            await make_request(self.session, HTTPMethod.POST, '/sendMessage', request),
        )


__all__ = [
    'BotAPI',
]
