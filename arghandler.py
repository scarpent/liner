import argparse

DEFAULT_LINE_LENGTH = 72


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
        '-c', '--clipboard',
        action='store_true',
        help='read/write text from clipboard',
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
