"""Types representing the bodies of API requests."""
from dataclasses import dataclass
from typing import List, Optional, Union

from .api_types import ChatID, MessageID, ParseMode, ReplyMarkup


@dataclass(frozen=True)
class SendMessageRequest:
    """Parameters for sending a message."""

    chat_id: Union[ChatID, str]
    text: str
    parse_mode: Optional[ParseMode] = None
    disable_web_page_preview: Optional[bool] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[MessageID] = None
    reply_markup: Optional[ReplyMarkup] = None


@dataclass(frozen=True)
class GetUpdatesRequest:
    """Parameters for getting updates for a bot."""

    offset: Optional[int] = None
    limit: Optional[int] = None
    timeout: Optional[int] = None
    allowed_updates: Optional[List[str]] = None
