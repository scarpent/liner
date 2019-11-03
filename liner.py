#!/usr/bin/python
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import codecs
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager

from arghandler import DEFAULT_LINE_LENGTH, get_args

LINED_SUFFIX = '_lined'
UTF_8 = 'utf-8'
BULLET_REGEX = r'^\s*([-*~+]|[#\d]+\.) '

line_length = DEFAULT_LINE_LENGTH


@contextmanager
def temp_file(data):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(data.encode(UTF_8))
    yield temp.name
    os.unlink(temp.name)


def is_non_block(line):
    patterns = [
        r'^[A-Za-z]+, \d{1,2} [A-Za-z]+ \d{4}$',  # date
        r'^`?(~<|>~)`?',                          # excerpts
        r'^\s*\|( |$)',                           # line quote
        r'^(\s*:|\.\. )',                         # rst items
        r'^[-#=~]{3,}$',                          # separator/heading
    ]

    return any(re.search(pattern, line) for pattern in patterns)


def is_bullet(line, para):
    return re.search(BULLET_REGEX, line)


def is_code_block_delimiter(line):
    return re.match(r'^```(?!`)', line)


def process_file(file_in, file_out):
    para = ''
    eol = ''
    block_in_progress = False
    code_block_in_progress = False

    for line in file_in:

        # last line may or may not have newline
        eol = '\n' if '\n' in line else ''

        line = line.rstrip()
        if (line == ''
                or is_non_block(line)
                or is_bullet(line, para)
                or is_code_block_delimiter(line)
                or code_block_in_progress):

            if block_in_progress:
                block_in_progress = False
                # [:-1] to trim trailing space
                write_paragraph(para[:-1], file_out, eol='\n')
                para = ''

            if is_code_block_delimiter(line):
                code_block_in_progress = not code_block_in_progress

            if code_block_in_progress or not is_bullet(line, para):
                write_paragraph(
                    line,
                    file_out,
                    eol=eol,
                    code_block_in_progress=code_block_in_progress
                )
                continue

        block_in_progress = True
        # join lines in a block together before lining/re-lining
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


def write_paragraph(para, file_out, eol='\n', code_block_in_progress=False):

    if para == '' or is_non_block(para) or code_block_in_progress:
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

    if is_bullet(para, ''):
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
    p.wait()
    data = p.stdout.read()
    return data.decode(UTF_8)


def set_clipboard_data(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data.encode(UTF_8))
    p.stdin.close()
    p.wait()


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

    args = get_args(argv)

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
        with temp_file(get_clipboard_data()) as tfile:
            temp_file_lined = tfile + LINED_SUFFIX

            process_file(
                get_file_in(tfile),
                get_file_out(temp_file_lined)
            )

        set_clipboard_data(read_file(temp_file_lined))
        os.remove(temp_file_lined)
    else:
        sys.stdout = codecs.getwriter(UTF_8)(sys.stdout)
        process_file(
            codecs.getreader(UTF_8)(sys.stdin),
            sys.stdout
        )


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
