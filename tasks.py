"""Linting module."""
import shlex
import subprocess
from dataclasses import dataclass
from functools import wraps
from typing import Callable, List, Optional, Union, overload

import typer
from typing_extensions import Literal

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


@dataclass
class CommandError:
    """Represent that a given command failed."""

    command_line: str
    exit_code: int


@dataclass
class CommandSuccess:
    """Represent that a given command ran successfully."""

    command_line: str


Result = Union[CommandError, CommandSuccess]


def check_commands(f: Callable[..., List[Result]]) -> Callable[..., List[Result]]:
    """Make a function that returns Results terminate the app if any of them failed."""

    @wraps(f)
    def _inner(*args, **kwargs) -> List[Result]:
        results = f(*args, **kwargs)

        failed_results = [r for r in results if isinstance(r, CommandError)]

        if failed_results:
            for failed in failed_results:
                print(
                    f'Command "{failed.command_line}" failed with error code '
                    f'{failed.exit_code}.'
                )
            raise typer.Exit(code=1)

        return results

    return _inner


@overload
def execute(
    command: Union[str, List[str]], *, raise_error: Literal[True] = True
) -> CommandSuccess:
    """Overload for when raise_error is True.

    In this case, we never return CommandError (we raise the subprocess
    exception)."""


@overload
def execute(command: Union[str, List[str]], *, raise_error: Literal[False]) -> Result:
    """Overload for when raise_error is True.

    In this case, we never raise, and instead we return CommandError."""


def execute(command: Union[str, List[str]], *, raise_error: bool = True) -> Result:
    """Echo and run a command."""
    command_str = command if isinstance(command, str) else ' '.join(command)
    print(f'### Executing: {command_str}')

    try:
        run_command(command)
    except subprocess.CalledProcessError as e:
        if raise_error:
            raise

        return CommandError(command_str, e.returncode)

    return CommandSuccess(command_str)


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
        ],
    )

    if not ci:
        execute('pre-commit install')


def test(
    coverage: bool = typer.Option(  # noqa: B008
        default=False, help='Generate coverage information.'
    ),
    html: bool = typer.Option(  # noqa: B008
        default=False, help='Generate an html coverage report.'
    ),
) -> List[Result]:
    """Run tests."""
    coverage_flag = [f'--cov={PACKAGE_NAME}'] if coverage else []

    return [
        execute(['pytest', *coverage_flag, 'tests'], raise_error=False),
        *(coverage_html() if coverage and html else ()),
    ]


APP.command()(check_commands(test))


def lint(
    files: Optional[List[str]] = typer.Argument(default=None,),  # noqa: B008
    *,
    full_report: bool = typer.Option(  # noqa: B008
        default=True, help='Print detailed reports.'
    ),
) -> List[Result]:
    """Run all linters.

    If files is omitted. everything is linted.
    """

    subject = files if files else EVERYTHING

    pylint_reports = ['-r', 'y'] if full_report else ['-r', 'n']

    return [
        execute(['mypy', *subject], raise_error=False),
        execute(['flake8', *subject], raise_error=False),
        execute(['pylint', *pylint_reports, *subject], raise_error=False),
    ]


APP.command()(check_commands(lint))


def format(  # pylint: disable=redefined-builtin
    files: Optional[List[str]] = typer.Argument(default=None),  # noqa: B008
    check: bool = typer.Option(  # noqa: B008
        default=False, help='Only checks instead of modifying.'
    ),
) -> List[Result]:
    """Run all formatters.

    If files is omitted. everything is linted.
    """

    black_check_flag = ['--check'] if check else []
    isort_check_flag = ['-c'] if check else []

    subject = files if files else EVERYTHING

    return [
        execute(['black', '-q', *black_check_flag, *subject], raise_error=False),
        execute(
            ['isort', '-rc', '-y', '-q', *isort_check_flag, *subject], raise_error=False
        ),
    ]


APP.command()(check_commands(format))


def coverage_html():
    """Generate an html coverage report."""
    return [
        execute(f'coverage html', raise_error=False),
    ]


APP.command()(check_commands(coverage_html))


def static_checks() -> List[Result]:
    """Run all static checks over all code."""
    return [
        *lint([]),
        *format([], check=True),
    ]


APP.command()(check_commands(static_checks))


def all_checks() -> List[Result]:
    """Run all checks (static checks and tests) over all code."""
    return [
        *static_checks(),
        *test(),
    ]


APP.command()(check_commands(all_checks))


if __name__ == '__main__':
    APP()
