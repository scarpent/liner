#!/usr/bin/python

"""unit tests for liner.py"""

import unittest

import liner


__author__ = "scarpent"
__date__ = "$Jun 30, 2016 6:00 PM$"


def read_file(filename):
    f = open(filename, 'r')
    filedata = f.read()
    f.close()
    return filedata

class Tests(unittest.TestCase):

    def setUp(self):
        self.save_clipboard = liner.getClipboardData()

    def tearDown(self):
        liner.setClipboardData(self.save_clipboard)

    def testMainFileInput(self):
        liner.main(['liner.py', '-f', 'test.txt'])
        expected = read_file('test.txt_lined_expected')
        actual = read_file('test.txt_lined')
        self.assertEqual(expected, actual)

    def testClipboard(self):
        expected = "Blah blah blah blah"
        liner.setClipboardData(expected)
        actual = liner.getClipboardData()
        self.assertEqual(expected, actual)

    def testLineLengthLessThanOne(self):
        expected = 'Lorem ipsum dolor sit amet'
        liner.setClipboardData(expected)
        liner.main(['liner.py', 0])
        actual = liner.getClipboardData()
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()         # pragma: no cover

