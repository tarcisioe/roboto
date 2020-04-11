Contributing
============

First steps
-----------

So you want to contribute to Roboto! Thanks! You will need:

- Python 3.7+
- Poetry (use the latest version)

To set up your develop environment, run:

```bash
python develop.py
```

and then poetry will be used to:

- Set up a virtual environment.
- Install `invoke` on it to run our basic development tasks
- Install `pre-commit` and set up pre-commit hooks

You can then activate your enviroment by running `poetry shell` (or prefix all
your commands with `poetry run`).


Static checkers
---------------

We expect a few static checkers to be clean, according to our project configs:

- Pylint (with `pylint-quotes`)
- Mypy
- Fláke8 (with `flake8-bugbear`)

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
- `inv static-checks`: includes formatting checks, does not change files.
- `inv lint`: same as before without format checks.
- `inv format`: formats code.


Running tests
-------------

We use `pytest` for our tests. The tests are located in the `tests` directory,
outside the main module, therefore the tests should import the main package
code through absolute imports.

To run tests use:

```bash
inv test
```

To run tests with coverage:

```bash
inv test --coverage
```


Checking coverage
-----------------

To check the code coverage with details, you can run

```
inv coverage-html
```

or run the tests like this:

```
inv test --coverage --html
```

and open `htmlcov/index.html` in your browser.
