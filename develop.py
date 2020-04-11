from argparse import ArgumentParser
from subprocess import run


def develop(test_only: bool, ci: bool):
    run(['poetry', 'install'], check=True)
    run(['poetry', 'run', 'pip', 'install', 'invoke'], check=True)

    if not test_only:
        ci_args = ['--ci'] if ci else []
        run(['poetry', 'run', 'inv', 'install-dev-tools', *ci_args], check=True)


def main(args):
    argparser = ArgumentParser()
    argparser.add_argument('--test-only', action='store_true', default=False)
    argparser.add_argument('--ci', action='store_true', default=False)
    ns = argparser.parse_args(args)

    develop(ns.test_only, ns.ci)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
