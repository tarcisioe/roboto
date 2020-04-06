"""Test for the `bot` module."""
from roboto.bot import BotAPI
from roboto.types import Token


def test_init_bot_api() -> None:
    """Ensure BotAPI derives its URL as needed."""
    api = BotAPI(Token('dummytoken'))

    assert api.api_url == 'https://api.telegram.org/botdummytoken/'
