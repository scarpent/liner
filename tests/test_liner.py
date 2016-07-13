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
        self.save_clipboard = liner.get_clipboard_data()

    def tearDown(self):
        liner.set_clipboard_data(self.save_clipboard)

    def testMainFileInput(self):
        liner.main(['liner.py', '-f', 'tests/test.txt'])
        expected = read_file('tests/test.txt_lined_expected')
        actual = read_file('tests/test.txt_lined')
        self.assertEqual(expected, actual)

    def testBullets(self):
        liner.main(['liner.py', '-f', 'tests/test_bullets.txt'])
        expected = read_file('tests/test_bullets.txt_lined_expected')
        actual = read_file('tests/test_bullets.txt_lined')
        self.assertEqual(expected, actual)

    def testNoEofNewline(self):
        liner.main(['liner.py', '-f', 'tests/test_eof_no_newline.txt'])
        expected = read_file(
            'tests/test_eof_no_newline.txt_lined_expected'
        )
        actual = read_file('tests/test_eof_no_newline.txt_lined')
        self.assertEqual(expected, actual)

    def testEofNewline(self):
        liner.main(['liner.py', '-f', 'tests/test_eof_newline.txt'])
        expected = read_file(
            'tests/test_eof_newline.txt_lined_expected'
        )
        actual = read_file('tests/test_eof_newline.txt_lined')
        self.assertEqual(expected, actual)

    def testJournalDate(self):
        liner.main(['liner.py', '-f', 'tests/test_journal_date.txt'])
        expected = read_file(
            'tests/test_journal_date.txt_lined_expected'
        )
        actual = read_file('tests/test_journal_date.txt_lined')
        self.assertEqual(expected, actual)

    def testExcerpt(self):
        liner.main(['liner.py', '-f', 'tests/test_excerpt.txt'])
        expected = read_file(
            'tests/test_excerpt.txt_lined_expected'
        )
        actual = read_file('tests/test_excerpt.txt_lined')
        self.assertEqual(expected, actual)

    def testLineQuote(self):
        liner.main(['liner.py', '-f', 'tests/test_line_quote.txt'])
        expected = read_file(
            'tests/test_line_quote.txt_lined_expected'
        )
        actual = read_file('tests/test_line_quote.txt_lined')
        self.assertEqual(expected, actual)

    def testRstItems(self):
        liner.main(['liner.py', '-f', 'tests/test_rst_items.txt'])
        expected = read_file(
            'tests/test_rst_items.txt_lined_expected'
        )
        actual = read_file('tests/test_rst_items.txt_lined')
        self.assertEqual(expected, actual)

    def testClipboard(self):
        expected = "Blah blah blah blah"
        liner.set_clipboard_data(expected)
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthLessThanOne(self):
        expected = 'Lorem ipsum dolor sit amet'
        liner.set_clipboard_data(expected)
        liner.main(['liner.py', 0])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthLessThanOneAndNewline(self):
        expected = 'Lorem ipsum dolor sit amet\n'
        liner.set_clipboard_data(expected)
        liner.main(['liner.py', 0])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthAsString(self):
        liner.set_clipboard_data('Lorem ipsum dolor sit amet')
        liner.main(['liner.py', "017"])
        expected = 'Lorem ipsum dolor\nsit amet'
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthBadString(self):
        liner.set_clipboard_data('Lorem ipsum dolor sit amet')
        liner.main(['liner.py', "abc"])
        expected = 'Lorem ipsum dolor sit amet'
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()         # pragma: no cover
