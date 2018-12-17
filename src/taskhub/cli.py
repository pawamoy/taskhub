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


def get_parser():
    parser = argparse.ArgumentParser()

    return parser


def main(args=None):
    parser = get_parser()
    args = parser.parse_args(args=args)

    return 0
