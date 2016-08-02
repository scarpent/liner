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
LINED_SUFFIX = '_lined'
TEMP_FILE_LINED = '{temp}_{suffix}'.format(
    temp=TEMP_FILE,
    suffix=LINED_SUFFIX
)
UTF_8 = 'utf-8'
BULLET_REGEX = r'^\s*[-*~] '

line_length = DEFAULT_LINE_LENGTH


def is_non_block(line):
    patterns = [
        r'^[A-Za-z]+, \d{1,2} [A-Za-z]+ \d{4}$',  # date
        r'^(~<|>~)',                              # excerpts
        r'^\s*\|( |$)',                           # line quote
        r'^(\s*:|\.\. )',                         # rst items
        r'^[-#=~]{3,}',                           # separator/heading
    ]

    for pattern in patterns:
        if re.search(pattern, line):
            return True

    return False


def is_bullet(line):
    if re.search(BULLET_REGEX, line):
        return True
    else:
        return False


def process_file(file_in, file_out):

    para = ''
    eol = ''
    block_in_progress = False

    for line in file_in:

        # last line may or may not have newline
        eol = '\n' if '\n' in line else ''

        line = line.rstrip()
        if line == '' or is_non_block(line) or is_bullet(line):
            if block_in_progress:
                block_in_progress = False
                # [:-1] to trim trailing space
                write_paragraph(para[:-1], file_out, eol='\n')
                para = ''

            if not is_bullet(line):
                write_paragraph(line, file_out, eol=eol)
                continue

        block_in_progress = True
        if para == '':
            # preserve leading spaces; first line indicates
            # blockquote indent for whole para (*if* a blockquote)
            #
            # also leading spaces important for bullets
            para += line + ' '
        else:
            para += line.strip() + ' '

    if para != '':
        write_paragraph(para[:-1], file_out, eol=eol)

    file_in.close()
    file_out.flush()
    file_out.close()


def write_paragraph(para, file_out, eol='\n'):

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

    if is_bullet(para):
        bullet_indent = re.sub(
            r'(' + BULLET_REGEX + r').*$',
            r'\1',
            para
        )
        new_indent = indent + re.sub(r'\S', ' ', bullet_indent)
        new_length = str(int(length) - 2)
    else:
        new_indent = None
        new_length = None

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

        if new_indent:
            indent = new_indent
            pattern = r'(.{0,' + new_length + r'}(?![^\s])|[^\s]+)\s*'
            r = re.compile(pattern)
            new_indent = None

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

    global line_length
    line_length = args.line_length

    if args.file:
        file_out = '{filepath}{suffix}'.format(
            filepath=args.file,
            suffix=LINED_SUFFIX
        )
        write_file(file_out, '')  # make sure is empty

        process_file(
            get_file_in(args.file),
            get_file_out(file_out)
        )
    elif args.clipboard:
        # clipboard uses files for consistent handling...
        write_file(TEMP_FILE, get_clipboard_data())
        write_file(TEMP_FILE_LINED, '')

        process_file(
            get_file_in(TEMP_FILE),
            get_file_out(TEMP_FILE_LINED)
        )

        set_clipboard_data(read_file(TEMP_FILE_LINED))
        os.remove(TEMP_FILE)
        os.remove(TEMP_FILE_LINED)
    else:
        sys.stdout = codecs.getwriter(UTF_8)(sys.stdout)
        process_file(
            codecs.getreader(UTF_8)(sys.stdin),
            sys.stdout
        )

if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
