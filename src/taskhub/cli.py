"""
Module that contains the command line application.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later,
  but that will cause problems: the code will get executed twice:

  - When you run `python -mtaskhub` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``taskhub.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``taskhub.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import argparse

from .core import services


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-service", dest="input_service", default="stdin")
    parser.add_argument("-o", "--output-service", dest="output_service", default="stdout")

    parser.add_argument("-s", "--srv-opt", "--service-option", dest="services_options", nargs=1)

    return parser


def main(args=None):
    parser = get_parser()
    args = parser.parse_args(args=args)

    input_service = services.SERVICES[args.input_service]
    output_service = services.SERVICES[args.output_service]

    data = input_service.read_tasks()
    output_service.write_tasks(data)

    return 0
