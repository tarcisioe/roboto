Roboto
======

![](https://github.com/tarcisioe/roboto/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/tarcisioe/roboto/branch/master/graph/badge.svg)](https://codecov.io/gh/tarcisioe/roboto)

A type-hinted async Telegram bot library, supporting `trio`, `curio` and `asyncio`.

Roboto's API is not perfectly stable nor complete yet. It will be kept a 0.x.0
until the Telegram Bot API is completely implemented, and will be bumped to
1.0.0 when it is complete.


Basic usage
===========

Roboto is still a low-level bot API, meaning it does not provide much
abstraction over the Bot API yet (that is planned, though).

Currently, a basic echo bot with roboto looks like:

```python
from roboto import Token, BotAPI
from trio import run  # This could be asyncio or curio as well!


api_token = Token('your-bot-token')


async def main() -> None:
    async with BotAPI.make(api_token) as bot:
        offset = 0

        while True:
            updates = await bot.get_updates(offset)

            for update in updates:
                if update.message is not None and update.message.text is not None:
                    await bot.send_message(
                        update.message.chat.id,
                        update.message.text,
                    )

            if updates:
                offset = updates[-1].update_id + 1


# In asyncio it should be "main()".
run(main)
```

Being statically-typed, Roboto supports easy autocompletion and `mypy` static
checking.


Contributing
------------

Check our [contributing guide](CONTRIBUTING.md) to know how to develop on
Roboto and contribute to our project.


Goals
=====

Principles
----------

- Ease of static checking for client code, especially static typing.
- Forwards compatibility (additions to the bot HTTP API should not break older
  versions of Roboto easily).

Achieved milestones
-------------------
- [X] Support for other async runtimes other than asyncio (especially
      [`trio`](https://github.com/python-trio/trio)) (done in 0.2.0).
- [X] All functions under [`Available methods` in the official
      documentation](https://core.telegram.org/bots/api#available-methods) (0.3.0).
- [X] All functions under [`Updating messages` in the official
      documentation](https://core.telegram.org/bots/api#updating-messages) (0.4.0).

Next milestones
---------------

- [ ] All functions under [`Stickers` in the
      documentation](https://core.telegram.org/bots/api#stickers) (0.5.0).
- [ ] [Inline mode
      functionality](https://core.telegram.org/bots/api#inline-mode) (0.6.0).
- [ ] [Payments functionality](https://core.telegram.org/bots/api#payments) (0.7.0).
- [ ] [Telegram Passport
      functionality](https://core.telegram.org/bots/api#telegram-passport) (0.8.0).
- [ ] [Games functionality](https://core.telegram.org/bots/api#games) (0.9.0).
- [ ] Tests for all bot API functions in `bot_tester`.
- [ ] Documentation with examples and tutorials.
- [ ] API documentation (automatically generated, likely with
      [Sphinx](https://www.sphinx-doc.org/en/master/)).
- [ ] API cleanup/streamlining (e.g. use kw-only arguments in bot methods) (1.0.0).
- [ ] High-level API (abstraction for command handlers, necessary internal
      state, etc.).


Acknowledgements
----------------

This used to be a disclaimer that we were vendoring
[asks](https://asks.readthedocs.io). We are not anymore (the feature we needed is
now on upstream), but I will still keep the acknowledgemente because it (through
[anyio](https://anyio.readthedocs.io)) gives us the ability to support the three
major async event loops, `asyncio`, `trio` and `curio`!
