#!/usr/bin/python
from __future__ import division
from __future__ import print_function
__author__ = 'Scott Carpenter'
__website__ = 'http://movingtofreedom.org'
__date__ = '$Mar 2, 2016 6:31 AM$'
__license__ = 'GPL v3+'

import sys
import re
import subprocess

TARGET_LINE_LENGTH=72

def getClipboardData():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = p.wait()
    data = p.stdout.read()
    return data

def setClipboardData(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    retcode = p.wait()

def isNonBlock(line):
    patterns = [
        r'^\s*[-*~] ',                          # bullets
        r'^[A-Za-z]+, \d+ [A-Za-z]+ \d+$',      # date
        r'^(~<|>~)',                            # excerpts
        r'^\s+\|',                              # line quote
        r'^(\s*:|\.\. )',                        # rst items
        r'^[-#=~]{3,}',                         # separator/heading
    ]

    for pattern in patterns:
        if re.search(pattern, line):
            #print('matched {p}'.format(p=pattern))
            return True

    return False

def handle(line_length):
    paragraphs = []
    para = ''
    block_in_progress = False

    # todo: file-based reading for larger files??
    # (journal never finishes this with 6K lines)
    lines = getClipboardData().split('\n')

    for line in lines:
        line = line.rstrip()
        if line == '' or isNonBlock(line):
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
        paragraphs.append(para)

    #[print('{para}'.format(para=para)) for para in paragraphs]
    #print(paragraphs)

    if line_length < 1:
        concatenated = ''
        for para in paragraphs:
            concatenated += '{para}\n'.format(para=para)
        setClipboardData(concatenated)
        return

    lined = ''
    for para in paragraphs:

        if para == '' or isNonBlock(para):
            lined += '{line}\n'.format(line=para)
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

            #print(m_match)
            lined += '{indent}{line}\n'.format(
                indent=indent,
                line=m_match
            )

            if m_end == len(para):  # infinite loop if
                break               #    m_start == m_end == len(para)
            elif m_start == m_end:  # zero-width match;
                m_end += 1          #    keep things moving along

            m = r.search(para, m_end)

    lined = lined[:-1]  # remove trailing newline

    setClipboardData(lined)

def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) > 1:
        handle(argv[1])
    else:
        handle(TARGET_LINE_LENGTH)

    return 0

if __name__ == '__main__':
    sys.exit(main())
