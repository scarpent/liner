#!/usr/bin/python

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import liner


__author__ = 'Scott Carpenter'
__license__ = 'gpl v3 or greater'
__email__ = 'scottc@movingtofreedom.org'


def get_expected_and_actual(testfile, line_length=None):
    testfile = 'tests/files/' + testfile
    if line_length:
        liner.main(['-f', testfile, '-l', line_length])
    else:
        liner.main(['-f', testfile])
    expected = liner.read_file(testfile + '_lined_expected')
    actual = liner.read_file(testfile + '_lined')
    return expected, actual


class Tests(unittest.TestCase):

    def setUp(self):
        self.save_clipboard = liner.get_clipboard_data()

    def tearDown(self):
        liner.set_clipboard_data(self.save_clipboard)

    def testMainFileInput(self):
        testfile = 'test.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testBullets(self):
        testfile = 'test_bullets.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testHeadings(self):
        testfile = 'test_headings.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testNoEofNewline(self):
        testfile = 'test_eof_no_newline.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testEofNewline(self):
        testfile = 'test_eof_newline.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testJournalDate(self):
        testfile = 'test_journal_date.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testExcerpt(self):
        testfile = 'test_excerpt.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testLineQuote(self):
        testfile = 'test_line_quote.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testIndent(self):
        testfile = 'test_indented.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testRstItems(self):
        testfile = 'test_rst_items.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testFileLineLength30(self):
        testfile = 'test_file_line_length_30.txt'
        expected, actual = get_expected_and_actual(testfile, '30')
        self.assertEqual(expected, actual)

    def testUtfDash8(self):
        """ utf8 encoding only "kind of" worked; utf-8 needed here """
        testfile = 'test_utf_dash_8.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testClipboard(self):
        expected = "Blah blah blah blah"
        liner.set_clipboard_data(expected)
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthLessThanOne(self):
        expected = 'Lorem ipsum dolor sit amet'
        liner.set_clipboard_data(expected)
        liner.main(['-l', 0])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthLessThanOneAndNewline(self):
        expected = 'Lorem ipsum dolor sit amet\n'
        liner.set_clipboard_data(expected)
        liner.main(['-l', '-1'])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthLessThanOneAndMultipleLines(self):
        """ lines are joined """
        expected = (
            'Vivamus sagittis lacus vel augue laoreet rutrum '
            'faucibus dolor auctor. Nullam quis risus eget urna '
            'mollis ornare vel eu leo.'
        )
        text = (
            'Vivamus sagittis lacus vel augue \nlaoreet rutrum '
            'faucibus dolor\nauctor. Nullam quis risus eget \n'
            'urna mollis ornare\nvel eu leo.'
        )
        liner.set_clipboard_data(text)
        liner.main(['-l', 0])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthAsString(self):
        liner.set_clipboard_data('Lorem ipsum dolor sit amet')
        liner.main(['-l', '017'])
        expected = 'Lorem ipsum dolor\nsit amet'
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testTrailingWhitespace(self):
        """ trailing whitespace is stripped """
        expected = '\n\nabc\n\n'
        text = ' \n\t\t\nabc \n    \n'
        liner.set_clipboard_data(text)
        liner.main(['-l', '50'])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()         # pragma: no cover

