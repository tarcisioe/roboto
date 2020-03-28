from typing import List

from invoke import Result, UnexpectedExit, task

PACKAGE_NAME="roboto"


def check_all(results: List[Result]):
    try:
        result = next(result for result in results if result.exited != 0)
    except StopIteration:
        pass
    else:
        raise UnexpectedExit(result)


@task
def test(c, coverage = False):
    coverage_flag = f'--cov={PACKAGE_NAME}' if coverage else None

    command = ' '.join(piece for piece in (
        'pytest',
        coverage_flag,
        'tests'
    ) if piece is not None)

    c.run(command)


@task
def lint(c):
    check_all([
        c.run(f'mypy {PACKAGE_NAME}'),
        c.run(f'flake8 {PACKAGE_NAME}'),
        c.run(f'pylint {PACKAGE_NAME}'),
        c.run(f'mypy tests'),
        c.run(f'flake8 tests'),
        c.run(f'pylint tests'),
    ])


@task
def format(c):
    c.run(f'black -q {PACKAGE_NAME}')
    c.run(f'black -q tests')
    c.run(f'isort -rc -y -q {PACKAGE_NAME}')
    c.run(f'isort -rc -y -q tests')


@task
def format_check(c):
    check_all([
        c.run(f'black --check -q {PACKAGE_NAME}', warn=True),
        c.run(f'black --check -q tests', warn=True),
        c.run(f'isort -rc -c -q {PACKAGE_NAME}', warn=True),
        c.run(f'isort -rc -c -q tests', warn=True),
    ])


@task
def all_checks(c):
    lint(c)
    format_check(c)
