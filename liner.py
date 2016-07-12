#!/usr/bin/python

from __future__ import division
from __future__ import print_function

import codecs
import os
import re
import subprocess
import sys

__author__ = 'Scott Carpenter'
__website__ = 'http://movingtofreedom.org'
__date__ = '$Mar 2, 2016 6:31 AM$'
__license__ = 'GPL v3+'


TARGET_LINE_LENGTH = 72
TEMP_FILE = 'liner_temp_file'


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


def handle(the_file, line_length=TARGET_LINE_LENGTH):
    paragraphs = []
    para = u''
    block_in_progress = False

    for line in the_file:
        line = line.rstrip()
        if line == u'' or is_non_block(line):
            if block_in_progress:
                block_in_progress = False
                paragraphs.append(para[:-1])
            paragraphs.append(line)
            para = u''
        else:
            block_in_progress = True
            if para == '':
                # preserve leading spaces; first line indicates
                # blockquote indent for whole para (*if* a blockquote)
                para += line + u' '
            else:
                para += line.strip() + u' '

    if para != u'':
        paragraphs.append(para[:-1])

    lined = u''

    if int(line_length) < 1:
        for para in paragraphs:
            lined += u'{para}\n'.format(para=para)
        return lined[:-1]

    for para in paragraphs:

        if para == u'' or is_non_block(para):
            lined += '{line}\n'.format(line=para)
            continue

        indent = re.sub(r'[^ ].*$', u'', para)
        if indent == u'':
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

            lined += u'{indent}{line}\n'.format(
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

    return lined


def get_file(filepath):
    return codecs.open(filepath, 'r', encoding='utf8')


def write_file(filepath, data):
    with codecs.open(filepath, 'w', encoding='utf8') as the_file:
        the_file.write(data)


def main(argv=None):

    if argv is None:
        argv = sys.argv  # pragma: no cover

    line_length = TARGET_LINE_LENGTH

    if len(argv) > 1:
        if argv[1] == '-f':
            fileloc = argv[2]
            # no line length option on files
            lined = handle(get_file(fileloc))
            write_file(
                '{filepath}_lined'.format(filepath=fileloc),
                lined
            )
            return 0
        else:
            try:
                line_length = int(argv[1])
            except ValueError:
                line_length = TARGET_LINE_LENGTH

    write_file(TEMP_FILE, get_clipboard_data())
    lined = handle(get_file(TEMP_FILE), line_length)
    set_clipboard_data(lined)
    os.remove(TEMP_FILE)
    return 0

if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
