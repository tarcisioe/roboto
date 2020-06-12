"""Module for running test bots for testing Roboto's API."""
from typing import Awaitable, Callable

import trio
import typer

from roboto import BotAPI, InlineKeyboardButton, InlineKeyboardMarkup, Token, Update

app = typer.Typer()


async def run_bot(token: str, handler: Callable[[BotAPI, Update], Awaitable[None]]):
    """Run a simple bot with a handler for its updates.

    Args:
        token: Token for the bot.
        handler: A handler that does something with an update.
    """
    async with BotAPI.make(Token(token)) as bot:
        offset = 0

        while True:
            updates = await bot.get_updates(offset)

            for update in updates:
                await handler(bot, update)

            if updates:
                offset = updates[-1].update_id + 1


async def callback_query_handler(bot: BotAPI, update: Update):
    """Test inline_keyboard with callback_query and answer_callback_query."""
    if update.message is not None and update.message.text is not None:
        await bot.send_message(
            update.message.chat.id,
            'A reply!',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text='Button', callback_data='button_pressed'
                        )
                    ]
                ]
            ),
        )

    if update.callback_query is not None:
        if update.callback_query.data == 'button_pressed':
            await bot.answer_callback_query(update.callback_query.id, 'Button pressed!')


@app.command()
def callback_query(token: str):
    """Run a bot with `callback_query_handler`."""
    trio.run(run_bot, token, callback_query_handler)


@app.callback()
def main():
    """This exists so we always have subcommands. May be removed when there are two."""


if __name__ == '__main__':
    app()
