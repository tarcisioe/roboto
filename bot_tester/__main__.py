"""Module for running test bots for testing Roboto's API."""
from typing import Awaitable, Callable

import trio
import typer

from roboto import (
    BotAPI,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Token,
    Update,
)

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


async def set_get_commands_bot(token: str):
    """Test setMyCommands and getMyCommands."""
    commands = [BotCommand('test', 'Test description.')]

    async with BotAPI.make(Token(token)) as bot:
        print('Setting commands as', commands)
        await bot.set_my_commands(commands)

        commands_from_server = await bot.get_my_commands()

        print('From server:', commands_from_server)
        assert commands_from_server == commands

        print('Clearing commands.')
        await bot.set_my_commands([])

        commands_from_server = await bot.get_my_commands()

        print('From server:', commands_from_server)
        assert commands_from_server == []


@app.command()
def set_get_commands(token: str):
    """Run a bot with `callback_query_handler`."""
    trio.run(set_get_commands_bot, token)


@app.callback()
def main():
    """This exists so we always have subcommands. May be removed when there are two."""


if __name__ == '__main__':
    app()
