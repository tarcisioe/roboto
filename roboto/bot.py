"""The main bot class for Roboto."""
from dataclasses import InitVar, dataclass, field
from typing import List, Optional, Union

from .datautil import from_json
from .http import HTTPMethod, make_request
from .types import (
    BotUser,
    ChatID,
    GetUpdatesRequest,
    Message,
    MessageID,
    ParseMode,
    SendMessageRequest,
    Token,
    Update,
)
from .url import URL


@dataclass
class BotAPI:
    """Bot API wrapper."""

    token: InitVar[Token]
    api_url: URL = field(init=False)

    def __post_init__(self, token: Token) -> None:
        """Constructor for bot objects.

        Args:
            token: The Bot API token.
        """
        self.api_url = URL.make(f'https://api.telegram.org/bot{token}/')

    async def get_me(self) -> BotUser:
        """getMe API method.

        Returns:
            User: the user object representing the bot itself.
        """
        return from_json(
            BotUser, await make_request(self.api_url, HTTPMethod.GET, 'getMe')
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
        response = await make_request(
            self.api_url, HTTPMethod.GET, 'getUpdates', request
        )
        return from_json(List[Update], response)

    async def send_message(
        self,
        chat_id: Union[ChatID, str],
        text: str,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[MessageID] = None,
    ) -> Message:
        """sendMessage API method.

        Args:
            chat_id: The ID of the chat to send a message to.
            text: The message text.
        """
        request = SendMessageRequest(
            chat_id,
            text,
            parse_mode,
            disable_web_page_preview,
            disable_notification,
            reply_to_message_id,
        )
        response = await make_request(
            self.api_url, HTTPMethod.POST, 'sendMessage', request
        )
        return from_json(Message, response)


__all__ = [
    'BotAPI',
]
