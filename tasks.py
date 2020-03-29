from dataclasses import dataclass
from typing import List

from invoke import Result, task

PACKAGE_NAME = "roboto"


@dataclass
class UnexpectedExits(Exception):
    failed_results: List[Result]

    def __repr__(self):
        return '\n'.join(repr(r) for r in self.failed_results)

    def __str__(self):
        return '\n'.join(str(r) for r in self.failed_results)


def check_all(results: List[Result]):
    results = [result for result in results if result.exited != 0]

    if results:
        raise UnexpectedExits(results)


@task
def test(c, coverage=False):
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
        c.run(f'mypy {PACKAGE_NAME}', warn=True, hide='out'),
        c.run(f'flake8 {PACKAGE_NAME}', warn=True, hide='out'),
        c.run(f'pylint {PACKAGE_NAME}', warn=True, hide='out'),
        c.run(f'mypy tests', warn=True, hide='out'),
        c.run(f'flake8 tests', warn=True, hide='out'),
        c.run(f'pylint tests', warn=True, hide='out'),
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
        c.run(f'black --check -q {PACKAGE_NAME}', warn=True, hide='out'),
        c.run(f'black --check -q tests', warn=True, hide='out'),
        c.run(f'isort -rc -c -q {PACKAGE_NAME}', warn=True, hide='out'),
        c.run(f'isort -rc -c -q tests', warn=True, hide='out'),
    ])


@task
def all_checks(c):
    lint(c)
    format_check(c)
