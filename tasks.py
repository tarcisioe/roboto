"""Linting module."""
import shlex
import subprocess
from typing import List, Optional, Union

import typer

PACKAGE_NAME = 'roboto'


def run_command(
    command: Union[str, List[str]], *args, **kwargs
) -> subprocess.CompletedProcess:
    """Wrapper for subprocess.run to support passing the command as a string."""
    split_command = shlex.split(command) if isinstance(command, str) else command
    return subprocess.run(split_command, check=True, *args, **kwargs)


def command_output(command: Union[str, List[str]]) -> str:
    """Run a command and get its stdout."""
    process = run_command(command, stdout=subprocess.PIPE)
    return process.stdout.decode('utf8')


def execute(command: Union[str, List[str]]) -> None:
    """Echo and run a command."""
    command_str = command if isinstance(command, str) else ' '.join(command)
    print(f'### Executing: {command_str}')
    run_command(command)


EVERYTHING = [
    'roboto',
    'tests',
    'develop.py',
    'tasks.py',
]
APP = typer.Typer()


@APP.command()
def install_dev_tools(
    ci: bool = typer.Option(  # noqa: B008
        default=False, help='Avoid installing tools that are unneeded for CI jobs.'
    )
):
    """Install development tools."""
    extra_deps = ['pre-commit'] if not ci else []

    execute(
        [
            'poetry',
            'run',
            'pip',
            'install',
            'black',
            'flake8',
            'flake8-bugbear',
            'isort',
            'mypy',
            'pylint',
            'pylint-quotes',
            *extra_deps,
        ]
    )

    if not ci:
        execute('pre-commit install')


@APP.command()
def test(
    coverage: bool = typer.Option(  # noqa: B008
        default=False, help='Generate coverage information.'
    ),
    html: bool = typer.Option(  # noqa: B008
        default=False, help='Generate an html coverage report.'
    ),
):
    """Run tests."""
    coverage_flag = [f'--cov={PACKAGE_NAME}'] if coverage else []

    execute(['pytest', *coverage_flag, 'tests'])

    if coverage and html:
        coverage_html()


@APP.command()
def lint(files: Optional[List[str]] = typer.Argument(default=None,)):  # noqa: B008
    """Run all linters.

    If files is omitted. everything is linted.
    """

    subject = files if files else EVERYTHING

    execute(['mypy', *subject])
    execute(['flake8', *subject])
    execute(['pylint', *subject])


@APP.command()
def format(  # pylint: disable=redefined-builtin
    files: Optional[List[str]] = typer.Argument(default=None),  # noqa: B008
    check: bool = typer.Option(  # noqa: B008
        default=False, help='Only checks instead of modifying.'
    ),
):
    """Run all formatters.

    If files is omitted. everything is linted.
    """

    black_check_flag = ['--check'] if check else []
    isort_check_flag = ['-c'] if check else []

    subject = files if files else EVERYTHING

    execute(['black', '-q', *black_check_flag, *subject])
    execute(['isort', '-rc', '-y', '-q', *isort_check_flag, *subject])


@APP.command()
def coverage_html():
    """Generate an html coverage report."""
    execute(f'coverage html')


@APP.command()
def static_checks():
    """Run all static checks over all code."""
    lint([])
    format([], check=True)


@APP.command()
def all_checks():
    """Run all checks (static checks and tests) over all code."""
    static_checks()
    test()


if __name__ == '__main__':
    APP()
