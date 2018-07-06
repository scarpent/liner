import io
import os
import sys
import unittest
from unittest import mock

import pytest

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__) + "/.."))

from liner import liner  # noqa: has to come after the sys path hack

TEST_FILES_DIR = 'tests/files/'
EXPECTED_SUFFIX = '{lined}_expected'.format(lined=liner.LINED_SUFFIX)


class FileTests(unittest.TestCase):

    @staticmethod
    def get_expected_and_actual(testfile, line_length=None):

        testfile = TEST_FILES_DIR + testfile

        if line_length:
            liner.main(['-f', testfile, '-l', line_length])
        else:
            liner.main(['-f', testfile])

        expected = liner.read_file(testfile + EXPECTED_SUFFIX)
        actual = liner.read_file(testfile + liner.LINED_SUFFIX)

        return expected, actual

    def test_main_file_input(self):
        testfile = 'test.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_bullets(self):
        testfile = 'test_bullets.txt'
        expected, actual = self.get_expected_and_actual(testfile, '40')
        self.assertEqual(expected, actual)

    def test_bullets_moar(self):
        testfile = 'test_bullets_moar.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_headings(self):
        testfile = 'test_headings.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_no_eof_newline(self):
        testfile = 'test_eof_no_newline.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_eof_newline(self):
        testfile = 'test_eof_newline.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_journal_date(self):
        testfile = 'test_journal_date.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_excerpt(self):
        testfile = 'test_excerpt.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_line_quote(self):
        testfile = 'test_line_quote.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_indent(self):
        testfile = 'test_indented.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_rst_items(self):
        testfile = 'test_rst_items.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_file_line_length_30(self):
        testfile = 'test_file_line_length_30.txt'
        expected, actual = self.get_expected_and_actual(testfile, '30')
        self.assertEqual(expected, actual)

    def test_utf_dash8(self):
        """ utf8 encoding only "kind of" worked; utf-8 needed here """
        testfile = 'test_utf_dash_8.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)

    def test_markdown_code_blocks(self):
        testfile = 'test_markdown_code_blocks.txt'
        expected, actual = self.get_expected_and_actual(testfile)
        self.assertEqual(expected, actual)


class ClipboardTests(unittest.TestCase):

    def setUp(self):
        self.save_clipboard = liner.get_clipboard_data()

    def tearDown(self):
        liner.set_clipboard_data(self.save_clipboard)

    def test_clipboard(self):
        expected = "Blah blah blah blah"
        liner.set_clipboard_data(expected)
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def test_line_length_less_than_one(self):
        expected = 'Lorem ipsum dolor sit amet'
        liner.set_clipboard_data(expected)
        liner.main(['-c', '-l', 0])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def test_line_length_less_than_one_and_newline(self):
        expected = 'Lorem ipsum dolor sit amet\n'
        liner.set_clipboard_data(expected)
        liner.main(['-c', '-l', '-1'])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def test_line_length_less_than_one_and_multiple_lines(self):
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
        liner.main(['-c', '-l', 0])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def test_line_length_as_string(self):
        liner.set_clipboard_data('Lorem ipsum dolor sit amet')
        liner.main(['-c', '-l', '017'])
        expected = 'Lorem ipsum dolor\nsit amet'
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def test_trailing_whitespace(self):
        """ trailing whitespace is stripped """
        expected = '\n\nabc\n\n'
        text = ' \n\t\t\nabc \n    \n'
        liner.set_clipboard_data(text)
        liner.main(['-c'])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)

    def test_utf8(self):
        expected = '\u2122 \u2122 \u2122\n\u2122 \u2122 \u2122\n\u2122'
        text = '\u2122 \u2122 \u2122 \u2122 \u2122 \u2122 \u2122'
        liner.set_clipboard_data(text)
        liner.main(['-c', '-l', '5'])
        actual = liner.get_clipboard_data()
        self.assertEqual(expected, actual)


class PipeTests(unittest.TestCase):

    def setUp(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout

    def tearDown(self):
        sys.stdin = self.stdin
        sys.stdout = self.stdout

    @staticmethod
    def get_expected_and_actual_pipe(testfile, line_length=None):

        testfile = TEST_FILES_DIR + testfile
        sys.stdin = open(testfile, 'r')
        sys.stdout = open(testfile + liner.LINED_SUFFIX, 'w')

        if line_length:
            liner.main(['-l', line_length])
        else:
            liner.main([])

        expected = liner.read_file(testfile + '_lined_expected')
        actual = liner.read_file(testfile + liner.LINED_SUFFIX)

        return expected, actual

    @pytest.mark.skip(reason='stopped working with python 3')
    def test_main_file_input_pipe(self):
        testfile = 'test_pipe.txt'
        expected, actual = self.get_expected_and_actual_pipe(testfile)
        self.assertEqual(expected, actual)

    @pytest.mark.skip(reason='stopped working with python 3')
    def test_bullets_pipe(self):
        testfile = 'test_bullets_pipe.txt'
        expected, actual = self.get_expected_and_actual_pipe(
            testfile,
            '40'
        )
        self.assertEqual(expected, actual)

    @pytest.mark.skip(reason='stopped working with python 3')
    def test_utf8_pipe(self):
        testfile = 'test_utf_dash_8_pipe.txt'
        expected, actual = self.get_expected_and_actual_pipe(testfile)
        self.assertEqual(expected, actual)

    @pytest.mark.skip(reason='stopped working with python 3')
    def test_file_line_length_30_pipe(self):
        testfile = 'test_file_line_length_30_pipe.txt'
        expected, actual = self.get_expected_and_actual_pipe(
            testfile,
            '30'
        )
        self.assertEqual(expected, actual)
