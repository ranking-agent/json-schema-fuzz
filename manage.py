#!/usr/bin/env python3
""" Management script to automate common commands """
import os
import sys


GREEN = '\033[92m'
ENDC = '\033[0m'


def print_green(text):
    """ Print text in green """
    print(f"{GREEN}{text}{ENDC}")


def run_command(cmd):
    """ Print and run command """
    print_green(cmd)
    os.system(cmd)


def test(extra_args):
    """
    This command runs the tests within docker
    and then exits.
    """
    command = """\
    docker build -t json-schema-fuzz-testing -f Dockerfile.test .
    docker run -it json-schema-fuzz-testing\
    """
    run_command(command + extra_args)


def coverage(extra_args):
    """
    Run tests in docker, copy out a coverage report,
    and display in browser
    """
    command = f"""\
    docker rm json-schema-fuzz-testing || true
    docker build -t json-schema-fuzz-testing \
                 -f Dockerfile.test .
    docker run --name json-schema-fuzz-testing json-schema-fuzz-testing \
            pytest --cov json_schema_fuzz/ --cov-report html {extra_args}
    docker cp json-schema-fuzz-testing:/app/htmlcov /tmp/json-schema-fuzz-cov/
    open /tmp/json-schema-fuzz-cov/index.html
    """
    run_command(command)


def main():
    """ Management script entrypoint """
    command = sys.argv[1]
    command_func = globals()[command]
    extra_args = " " + " ".join(sys.argv[2:])
    command_func(extra_args)


if __name__ == '__main__':
    main()
