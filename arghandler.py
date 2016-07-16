#!/usr/bin/python

from __future__ import print_function

import argparse


__author__ = 'Scott Carpenter'
__license__ = 'gpl v3 or greater'
__email__ = 'scottc@movingtofreedom.org'


DEFAULT_LINE_LENGTH = 72


class ArgHandler(object):

    @staticmethod
    def get_args(args):
        parser = argparse.ArgumentParser(
            prog='liner.py',
            formatter_class=(
                lambda prog: argparse.ArgumentDefaultsHelpFormatter(
                    prog,
                    max_help_position=30
                )
            )
        )

        parser.add_argument(
            '-f', '--file',
            type=str,
            help='file to be lined',
        )

        parser.add_argument(
            '-l', '--line-length',
            type=int,
            metavar='LEN',
            default=DEFAULT_LINE_LENGTH,
            help='line length; if less than 1, join lines and exit',
        )

        return parser.parse_args(args)
