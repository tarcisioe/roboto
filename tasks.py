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
def format(c):
    c.run(f"black -q {PACKAGE_NAME}")
    c.run(f"isort -rc -y -q {PACKAGE_NAME}")


@task
def format_check(c):
    check_all([
        c.run(f"black --check -q {PACKAGE_NAME}", warn=True),
        c.run(f"isort -rc -c -q {PACKAGE_NAME}", warn=True),
    ])
