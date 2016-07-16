#!/usr/bin/python

"""unit tests for liner.py"""

import codecs
import unittest

import liner


__author__ = "scarpent"
__date__ = "$Jun 30, 2016 6:00 PM$"


def read_file(filename):
    f = codecs.open(filename, 'r', encoding='utf-8')
    filedata = f.read()
    f.close()
    return filedata


def get_expected_and_actual(testfile):
    liner.main(['liner.py', '-f', testfile])
    expected = read_file(testfile + '_lined_expected')
    actual = read_file(testfile + '_lined')
    return expected, actual


class Tests(unittest.TestCase):

    def setUp(self):
        self.save_clipboard = liner.get_clipboard_data()

    def tearDown(self):
        liner.set_clipboard_data(self.save_clipboard)

    def testMainFileInput(self):
        testfile = 'tests/test.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testBullets(self):
        testfile = 'tests/test_bullets.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testHeadings(self):
        testfile = 'tests/test_headings.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testNoEofNewline(self):
        testfile = 'tests/test_eof_no_newline.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testEofNewline(self):
        testfile = 'tests/test_eof_newline.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testJournalDate(self):
        testfile = 'tests/test_journal_date.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testExcerpt(self):
        testfile = 'tests/test_excerpt.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testLineQuote(self):
        testfile = 'tests/test_line_quote.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testRstItems(self):
        testfile = 'tests/test_rst_items.txt'
        expected, actual = get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def testUtfDash8(self):
        """ utf8 encoding only "kind of" worked; utf-8 needed here """
        testfile = 'tests/test_utf_dash_8.txt'
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
        liner.main(['liner.py', 0])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def testLineLengthLessThanOneAndNewline(self):
        expected = 'Lorem ipsum dolor sit amet\n'
        liner.set_clipboard_data(expected)
        liner.main(['liner.py', 0])
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

