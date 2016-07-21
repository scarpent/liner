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


TEMP_FILE = '{home}/.liner_temp_file'.format(
    home=os.path.expanduser('~')
)
TEMP_FILE_LINED = '{temp}_lined'.format(temp=TEMP_FILE)
LINED_SUFFIX = '_lined'
UTF_8 = 'utf-8'


def is_non_block(line):
    patterns = [
        r'^[A-Za-z]+, \d{1,2} [A-Za-z]+ \d{4}$', # date
        r'^(~<|>~)',                             # excerpts
        r'^\s*\|( |$)',                          # line quote
        r'^(\s*:|\.\. )',                        # rst items
        r'^[-#=~]{3,}',                          # separator/heading
    ]

    for pattern in patterns:
        if re.search(pattern, line):
            return True

    if is_bullet(line):
        return True

    return False

def is_bullet(line):
    if re.search(r'^\s*[-*~] ', line):
        return True
    else:
        return False


def line_the_file(file_in, file_out, line_length=DEFAULT_LINE_LENGTH):

    para = ''
    eol = ''
    block_in_progress = False

    for line in file_in:

        # last line may or may not have newline
        eol = '\n' if '\n' in line else ''

        line = line.rstrip()
        if line == '' or is_non_block(line):
            if block_in_progress:
                block_in_progress = False
                # [:-1] to trim trailing space
                write_paragraph(
                    para[:-1],
                    file_out,
                    eol='\n',
                    line_length=line_length
                )
            write_paragraph(
                line,
                file_out,
                eol=eol,
                line_length=line_length
            )
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
        write_paragraph(
            para[:-1],
            file_out,
            eol=eol,
            line_length=line_length
        )

    file_in.close()
    file_out.flush()
    file_out.close()


def write_paragraph(
    para,
    file_out,
    eol='\n',
    line_length=DEFAULT_LINE_LENGTH
):

    if para == '' or is_non_block(para):
        file_out.write(para + eol)
        return

    if int(line_length) < 1:
        # if less than one, use the joined line
        file_out.write(para + eol)
        return

    indent = re.sub(r'[^ ].*$', '', para)
    if indent == '':
        length = str(line_length)
    else:
        para = para.lstrip()
        length = str(line_length - len(indent))

    pattern = r'(.{0,' + length + r'}(?![^\s])|[^\s]+)\s*'
    r = re.compile(pattern)
    m = r.search(para)

    lined = ''
    while m:  # will always be at least one m w/ logic above
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

    # remove assumed trailing newline from loop and add back eol
    file_out.write(lined[:-1] + eol)


def get_clipboard_data():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = p.wait()
    data = p.stdout.read()
    return data.decode(UTF_8)


def set_clipboard_data(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data.encode(UTF_8))
    p.stdin.close()
    retcode = p.wait()


def get_file_in(filepath):
    return codecs.open(filepath, 'r', encoding=UTF_8)


def get_file_out(filepath):
    return codecs.open(filepath, 'w', encoding=UTF_8)


def read_file(filepath):
    with codecs.open(filepath, 'r', encoding=UTF_8) as the_file:
        return the_file.read()


def write_file(filepath, data):
    with codecs.open(filepath, 'w', encoding=UTF_8) as the_file:
        the_file.write(data)


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]  # pragma: no cover

    args = ArgHandler.get_args(argv)

    if args.file:
        file_out = '{filepath}{suffix}'.format(
            filepath=args.file,
            suffix=LINED_SUFFIX
        )
        write_file(file_out, '')  # make sure is empty

        line_the_file(
            get_file_in(args.file),
            get_file_out(file_out),
            args.line_length
        )
    elif args.clipboard:
        # clipboard uses files for consistent handling...
        write_file(TEMP_FILE, get_clipboard_data())
        write_file(TEMP_FILE_LINED, '')

        line_the_file(
            get_file_in(TEMP_FILE),
            get_file_out(TEMP_FILE_LINED),
            args.line_length
        )

        set_clipboard_data(read_file(TEMP_FILE_LINED))
        os.remove(TEMP_FILE)
        os.remove(TEMP_FILE_LINED)
    else:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
        line_the_file(
            codecs.getreader('utf-8')(sys.stdin),
            sys.stdout,
            args.line_length
        )

if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
