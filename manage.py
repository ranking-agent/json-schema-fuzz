#!/usr/bin/env python3
import sys
import os


def print_green(s):
    GREEN = '\033[92m'
    ENDC = '\033[0m'
    print(f"{GREEN}{s}{ENDC}")


def run_command(cmd):
    print_green(cmd)
    os.system(cmd)


def test(extra_args):
    """
    This command runs the tests within docker
    and then exits.
    """
    command = """\
    docker build -t strider-testing -f Dockerfile.test .
    docker run -it strider-testing\
    """
    run_command(command + extra_args)


def coverage(extra_args):
    """
    Run tests in docker, copy out a coverage report,
    and display in browser
    """
    command = f"""\
    docker rm strider-testing || true
    docker build -t strider-testing \
                 -f Dockerfile.test .
    docker run --name strider-testing strider-testing \
            pytest --cov strider/ --cov-report html {extra_args}
    docker cp strider-testing:/app/htmlcov /tmp/strider-cov/
    open /tmp/strider-cov/index.html
    """
    run_command(command)


def main():
    command = sys.argv[1]
    command_func = globals()[command]
    extra_args = " " + " ".join(sys.argv[2:])
    command_func(extra_args)


if __name__ == '__main__':
    main()
