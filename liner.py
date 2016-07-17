#!/usr/bin/python

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import os
import re
import subprocess
import sys

from arghandler import ArgHandler
from arghandler import DEFAULT_LINE_LENGTH


__author__ = 'Scott Carpenter'
__license__ = 'gpl v3 or greater'
__email__ = 'scottc@movingtofreedom.org'
__date__ = '$Mar 2, 2016 6:31 AM$'


TEMP_FILE = 'liner_temp_file'
TEMP_FILE_LINED = '{temp}_lined'.format(temp=TEMP_FILE)


def is_non_block(line):
    patterns = [
        r'^\s*[-*~] ',                          # bullets
        r'^[A-Za-z]+, \d+ [A-Za-z]+ \d+$',      # date
        r'^(~<|>~)',                            # excerpts
        r'^\s+\|',                              # line quote
        r'^(\s*:|\.\. )',                       # rst items
        r'^[-#=~]{3,}',                         # separator/heading
    ]

    for pattern in patterns:
        if re.search(pattern, line):
            return True

    return False


def handle(file_in, file_out, line_length=DEFAULT_LINE_LENGTH):
    paragraphs = []
    para = ''
    block_in_progress = False
    trailing_newline = False

    for line in file_in:

        # we'll want to know this for last line in file
        trailing_newline = '\n' in line

        line = line.rstrip()
        if line == '' or is_non_block(line):
            if block_in_progress:
                block_in_progress = False
                paragraphs.append(para[:-1])
            paragraphs.append(line)
            para = ''
        else:
            block_in_progress = True
            if para == '':
                # preserve leading spaces; first line indicates
                # blockquote indent for whole para (*if* a blockquote)
                para += line + ' '
            else:
                para += line.strip() + ' '

    if para != '':
        paragraphs.append(para[:-1])

    lined = ''

    for para in paragraphs:

        if para == '' or is_non_block(para):
            lined += '{line}\n'.format(line=para)
            continue

        if int(line_length) < 1:
            # if less than one, return the joined lines
            lined += '{para}\n'.format(para=para)
            continue

        indent = re.sub(r'[^ ].*$', '', para)
        if indent == '':
            length = str(line_length)
        else:
            para = para.lstrip()
            length = str(line_length - len(indent))

        pattern = r'(.{0,' + length + r'}(?![^\s])|[^\s]+)\s*'
        r = re.compile(pattern)
        m = r.search(para)

        while m:
            m_start = m.start()
            m_end = m.end()
            m_match = para[m_start:m_end]

            lined += '{indent}{line}\n'.format(
                indent=indent,
                line=m_match.rstrip()
            )

            if m_end == len(para):
                # infinite loop if m_start == m_end == len(para)
                break
            elif m_start == m_end:
                # zero-width match; keep things moving along
                # (this may be impossible with our regex)
                m_end += 1  # pragma: no cover

            m = r.search(para, m_end)

    lined = lined[:-1]  # remove trailing newline

    # put back trailing line if original file had it
    if trailing_newline:
        lined += '\n'

    return lined


def get_clipboard_data():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = p.wait()
    data = p.stdout.read()
    return data


def set_clipboard_data(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    retcode = p.wait()


def get_file_in(filepath):
    return codecs.open(filepath, 'r', encoding='utf-8')


def get_file_out(filepath):
    return codecs.open(filepath, 'w', encoding='utf-8')


def read_file(filepath):
    with codecs.open(filepath, 'r', encoding='utf-8') as the_file:
        return the_file.read()


def write_file(filepath, data):
    with codecs.open(filepath, 'w', encoding='utf-8') as the_file:
        the_file.write(data)


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]  # pragma: no cover

    args = ArgHandler.get_args(argv)

    if args.file:
        file_out = '{filepath}_lined'.format(filepath=args.file)
        write_file(file_out, '')  # make sure is empty
        handle(
            get_file_in(args.file),
            get_file_out(file_out),
            args.line_length
        )
    else:
        write_file(TEMP_FILE, get_clipboard_data())
        write_file(TEMP_FILE_LINED, '')
        handle(
            get_file_in(TEMP_FILE),
            get_file_out(TEMP_FILE_LINED),
            args.line_length
        )
        set_clipboard_data(read_file(TEMP_FILE_LINED))
        os.remove(TEMP_FILE)
        os.remove(TEMP_FILE_LINED)

if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
