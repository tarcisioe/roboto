"""Module for running test bots for testing Roboto's API."""
from pathlib import Path
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
    """Test inline keyboard with callback query and answer_callback_query."""
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
    """Run a bot that answers callback queries from an inline keyboard."""
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
    """Run a bot that tests setMyCommands and getMyCommands."""
    trio.run(set_get_commands_bot, token)


async def send_delete_message_handler(bot: BotAPI, update: Update):
    """Test sendMessage and deleteMessage."""

    if update.message is not None and update.message.text is not None:
        msg = await bot.send_message(
            update.message.chat.id, 'This message will self-destruct in 5 seconds',
        )
        await trio.sleep(5)
        await bot.delete_message(update.message.chat.id, msg.message_id)


@app.command()
def send_delete_message(token: str):
    """Run a bot that tests sendMessage and deleteMessage"""
    trio.run(run_bot, token, send_delete_message_handler)


async def send_edit_message_handler(bot: BotAPI, update: Update):
    """Test sendMessage and editMessageText."""

    if update.message is not None and update.message.text is not None:
        msg = await bot.send_message(
            update.message.chat.id, 'This message will be edited in 5 seconds',
        )
        await trio.sleep(5)
        await bot.edit_message_text(
            update.message.chat.id, msg.message_id, 'This message was edited.',
        )


@app.command()
def send_edit_message(token: str):
    """Run a bot that tests sendMessage and editMessageText"""
    trio.run(run_bot, token, send_edit_message_handler)


async def edit_photo_caption_handler(bot: BotAPI, update: Update, photo: Path):
    """Test sendPhoto and editMessageCaption."""

    if update.message is not None and update.message.text is not None:
        msg = await bot.send_photo(
            update.message.chat.id,
            photo,
            caption='This caption will be edited in 5 seconds',
        )
        await trio.sleep(5)
        await bot.edit_message_caption(
            update.message.chat.id,
            msg.message_id,
            'This caption will be removed in 5 seconds.',
        )
        await trio.sleep(5)
        await bot.edit_message_caption(
            update.message.chat.id, msg.message_id,
        )


@app.command()
def edit_photo_caption(token: str, photo: Path):
    """Run a bot that tests sendPhoto and editMessageCaption"""
    trio.run(run_bot, token, lambda b, u: edit_photo_caption_handler(b, u, photo))


if __name__ == '__main__':
    typer.main.get_command(app)(prog_name=__package__)
