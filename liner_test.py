#!/usr/bin/python

"""unit tests for liner.py"""

import unittest
import os
import sys

from StringIO import StringIO

import liner


__author__ = "scarpent"
__date__ = "$Jun 30, 2016 6:00 PM$"


def read_file(filename):
    f = open(filename, 'r')
    filedata = f.read()
    f.close()
    return filedata

class MainFileInput(unittest.TestCase):

    def testMainFileInput(self):
        liner.main([
            'liner.py',
            '-f',
            'test.txt'
        ])

        expected = read_file('test.txt_lined_expected')
        actual = read_file('test.txt_lined')

        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()         # pragma: no cover

