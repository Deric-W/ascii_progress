#!/usr/bin/python3

"""Tests for the spinner submodule"""

import unittest
import unittest.mock
from io import StringIO
from ascii_progress.spinner import Spinner


class TestSpinner(unittest.TestCase):
    """tests for Spinner"""

    def test_eq(self) -> None:
        """test Spinner.__eq__"""
        output1 = StringIO()
        output2 = StringIO()
        spinners = [
            Spinner("abc", output1),
            Spinner("cba", output1),
            Spinner("abc", output2),
            Spinner("abc", output1),
            Spinner("abc", output1)
        ]
        spinners[-2].set_progress(1)
        spinners[-1].current_padding = -42
        for spinner in spinners:
            self.assertEqual(
                [s for s in spinners if s == spinner],
                [spinner]
            )
        self.assertNotEqual(spinners[0], 42)

    def test_context(self) -> None:
        """test Spinner __enter__ and __exit__"""
        output = StringIO()
        with Spinner("abc", output) as spinner:
            self.assertIsInstance(spinner, Spinner)
            self.assertEqual(output.getvalue(), "a")
        self.assertEqual(output.getvalue(), "a\bFinished\n")
        output.seek(0)
        output.truncate(0)
        with self.assertRaises(KeyboardInterrupt):
            with Spinner("abc", output) as spinner:
                raise KeyboardInterrupt
        self.assertEqual(output.getvalue(), "a\b\b\bKeyboardInterrupt  \n")

    def test_iter(self) -> None:
        """test Spinner __iter__ and __exit__"""
        output = StringIO()
        with Spinner("abc", output) as spinner:
            for _ in zip(range(6), spinner):
                pass
        self.assertEqual(output.getvalue(), "a\bb\bc\ba\bb\bc\ba\bFinished\n")

    def test_with_padding(self) -> None:
        """test Spinner.with_padding"""
        self.assertEqual(
            Spinner.with_padding(("a", "42", "c"), StringIO()).frames,
            ("a ", "42", "c ")
        )

    def test_current_frame(self) -> None:
        """test Spinner.current_frame"""
        output = StringIO()
        with Spinner("abc", output) as spinner:
            self.assertEqual(spinner.current_frame, "a")
            spinner.set_progress(1)
            self.assertEqual(spinner.current_frame, "b")
            spinner.current_frame = "a"
            with self.assertRaises(ValueError):
                spinner.current_frame = "x"
        self.assertEqual(output.getvalue(), "a\bb\ba\bFinished\n")

    def test_update(self) -> None:
        """test Spinner.update"""
        output = unittest.mock.Mock(
            wraps=StringIO()
        )
        spinner = Spinner(("ab", "c"), output)
        output.flush.assert_called_once()
        spinner.update(0)
        spinner.update(1)
        spinner.update(0)
        with self.assertRaises(IndexError):
            spinner.update(42)
        self.assertEqual(output.flush.call_count, 4)
        self.assertEqual(output.getvalue(), "ab\b\bab\b\bc \b\bab")

    def test_reset(self) -> None:
        output = StringIO()
        spinner = Spinner(("ab", "c"), output)
        spinner.set_progress(1)
        spinner.reset()
        self.assertEqual(output.getvalue(), "ab\b\bc \b\b")

    def test_set_progress(self) -> None:
        """test Spinner.set_progress"""
        output = StringIO()
        with Spinner("abc", output) as spinner:
            spinner.set_progress(2)
            spinner.set_progress(4)
        self.assertEqual(output.getvalue(), "a\bc\bb\bFinished\n")

    def test_replace(self) -> None:
        """test Spinner.replace"""
        output = unittest.mock.Mock(
            wraps=StringIO()
        )
        Spinner(("testtest", ""), output).replace("test", "42")
        self.assertEqual(output.flush.call_count, 2)
        self.assertEqual(output.getvalue(), "testtest\b\b\b\b\b\b\b\btest    42")
