Contributing
============

First steps
-----------

So you want to contribute to Roboto! Thanks! You will need:

- Python 3.7+
- Poetry (use the latest version)

To set up your develop environment, run:

```bash
$ python develop.py
```

and then poetry will be used to:

- Set up a virtual environment.
- Install `typer` on it to enable our basic development tasks script
- Install `pre-commit` and set up pre-commit hooks

You can then activate your enviroment by running `poetry shell` (or prefix all
your commands with `poetry run`).


Static checkers
---------------

We expect a few static checkers to be clean, according to our project configs:

- Pylint (with `pylint-quotes`)
- Mypy
- Flake8 (with `flake8-bugbear`)

Those will run on the CI, therefore they should be clean. They will be run by
pre-commit, so if you set your environment correctly, you should have no
issues.


Code style
----------

We follow the PEP-8 and use `black` to format our code and `isort` to sort
imports.  Those are run by pre-commit, so again, if everything is well set
there should be no issue.


Manually running checks
-----------------------

You can manually run:
- `python -m tasks static-checks`: includes formatting checks, does not change files.
- `python -m tasks lint`: same as before without format checks.
- `python -m tasks format`: formats code.


Running tests
-------------

We use `pytest` for our tests. The tests are located in the `tests` directory,
outside the main module, therefore the tests should import the main package
code through absolute imports.

To run tests use:

```bash
$ python -m tasks test
```

To run tests with coverage:

```bash
$ python -m tasks test --coverage
```


Checking coverage
-----------------

To check the code coverage with details, you can run

```bash
$ python -m tasks coverage-html
```

or run the tests like this:

```bash
$ python -m tasks test --coverage --html
```

and open `htmlcov/index.html` in your browser.


`bot_tester`
------------

The `bot_tester` package provides a way for running a real Telegram bot to test
certain API features. If something new on the API is implemented, it surely
deserves a test there.

This package is not run on the CI, because it demands user interaction through
Telegram.  It is linted and type-checked, though. So our CI should complain if
it is somehow broken.

Right now, not all API features are tested there. This was introduced late in
development, so one of our milestones is actually having tests for everything
we can there.

To run the `bot_tester`, you must use

```bash
$ python -m bot_tester <subcommand> <token>
```

Where `subcommand` is the function you want to run, and Token is the token for
a bot to use for testing. You can create one with @botfather on telegram.

You can also use `python -m bot_tester --help` to list all available test functions.
