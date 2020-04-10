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
      [`trio`](https://github.com/python-trio/trio)) (done in v0.2.0).

Next milestones
---------------

- [ ] Full Telegram Bot API implementation.
- [ ] High-level API (abstraction for command handlers, necessary internal
      state, etc.).

