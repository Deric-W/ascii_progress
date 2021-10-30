#!/usr/bin/python3

"""Tests for bar submodule"""

import unittest
import unittest.mock
from io import StringIO
from typing import ContextManager
from ascii_progress.bar import (
    LAZY_FORMATTER,
    BarContext,
    Bar,
    ASCIIBar,
    ThresholdDecorator,
    PercentDecorator,
    BarDecorator,
    BarFormat
)


class TestLazyFormatter(unittest.TestCase):
    """Tests for LazyFormatter"""

    def test_get_value(self) -> None:
        """test LazyFormatter.get_value"""
        self.assertEqual(
            LAZY_FORMATTER.get_value(0, (lambda: 42, lambda: self.fail("called wrong function")), {}),
            42
        )
        self.assertEqual(
            LAZY_FORMATTER.get_value("42", tuple(), {"42": lambda: 0, "a": lambda: self.fail("called wrong function")}),
            0
        )
        with self.assertRaises(IndexError):
            LAZY_FORMATTER.get_value(1, tuple(), {})
        with self.assertRaises(KeyError):
            LAZY_FORMATTER.get_value("a", tuple(), {})

    def test_format(self) -> None:
        """test LazyFormatter.format"""
        self.assertEqual(
            LAZY_FORMATTER.format("a{}c{d}", lambda: "b", d=lambda: "d"),
            "abcd"
        )


class BarSpinnerContext(unittest.TestCase):
    """tests for BarContext"""

    def test_eq(self) -> None:
        """test BarContext.__eq__"""
        format = BarFormat(("-[", "]-"), ("  ", "=="), 5)
        bar = ASCIIBar(format, file=StringIO())
        contexts = [
            BarContext(bar, "1", "2"),
            BarContext(bar, "2", "2"),
            BarContext(bar, "1", "1"),
            BarContext(ASCIIBar(format, file=StringIO()), "1", "1")
        ]
        for context in contexts:
            self.assertEqual(
                [context],
                [c for c in contexts if c == context]
            )
        self.assertNotEqual(contexts[0], 42)

    def test_context(self) -> None:
        """test SpinnerContext as context manager"""
        output = StringIO()
        bar = ASCIIBar(BarFormat(("[", "]"), (" ", "="), 3, format="{bar}"), file=output)
        with BarContext(bar, "1", "2") as context:
            self.assertIsInstance(context, Bar)
            context.set_progress(34)
            context.update()
        with self.assertRaises(RuntimeError):
            with BarContext(bar, "1", "2") as context:
                context.set_progress(67)
                context.update()
                raise RuntimeError
        with self.assertRaises(KeyboardInterrupt):
            with BarContext(bar, "1", "2") as context:
                context.set_progress(100)
                context.update()
                raise KeyboardInterrupt
        self.assertEqual(
            output.getvalue(),
            "\b\b\b\b\b".join((
                "[   ]",
                "[=  ]",
                "1    \n",
                "[== ]",
                "2    \n",
                "[===]",
                "\b\b2      \n"
            ))
        )


class TestBar(unittest.TestCase):
    """Tests for Bar"""

    def test_eq(self) -> None:
        """test Bar.__eq__"""
        format = BarFormat(("-[", "]-"), ("  ", "=="), 5)
        bars = [
            ASCIIBar(format, file=StringIO(), max=100),
            ASCIIBar(BarFormat(("-[", "]-"), ("  ", "=="), 10), file=StringIO(), max=100),
            ASCIIBar(format, file=StringIO(), max=10)
        ]
        bars[0].set_progress(10)
        for bar in bars:
            self.assertEqual(
                [bar],
                [b for b in bars if Bar.__eq__(bar, b)]
            )
        self.assertIs(Bar.__eq__(bars[0], 42), NotImplemented)

    def test_iter(self) -> None:
        """test Bar.__iter__ and __next__"""
        mock = unittest.mock.Mock(spec=Bar)
        mock.set_progress.configure_mock(side_effect=lambda p: p <= 10)
        progress = iter(range(100))
        mock.progress.configure_mock(side_effect=lambda: next(progress))
        self.assertIs(Bar.__iter__(mock), mock)
        iterations = iter(range(13))
        for _ in iterations:
            try:
                Bar.__next__(mock)
            except StopIteration:
                break
        self.assertEqual(next(iterations), 11)

    def test_handle_exceptions(self) -> None:
        """test Bar.handle_exceptions"""
        self.assertIsInstance(
            Bar.handle_exceptions(None, "", ""),
            ContextManager
        )


class TestASCIIBar(unittest.TestCase):
    """Tests for ASCIIBar"""

    FORMAT = BarFormat(("[", "]"), (" ", "="), 10)

    def test_eq(self) -> None:
        """test ASCIIBar.__eq__"""
        output = StringIO()
        bars = [
            ASCIIBar(self.FORMAT, max=100, file=output),
            ASCIIBar(BarFormat(("[", "]"), (" ", "="), 5), max=100, file=output),
            ASCIIBar(self.FORMAT, max=10, file=output),
            ASCIIBar(self.FORMAT, max=100, file=StringIO())
        ]
        bars[0].set_progress(10)
        for bar in bars:
            self.assertEqual(
                [bar],
                [b for b in bars if b == bar]
            )
        self.assertNotEqual(bars[0], 42)

    def test_update(self) -> None:
        """test ASCIIBar.update"""
        output = unittest.mock.Mock(wraps=StringIO())
        bar = ASCIIBar(self.FORMAT, max=100, file=output)
        output.reset_mock()
        bar.set_progress(42)
        output.write.assert_not_called()
        bar.update()
        output.write.assert_called()
        output.flush.assert_called()
        bar.set_progress(10)
        bar.update()
        self.assertEqual(
            output.getvalue(),
            ("\b" * 25).join((
                "[          ]   0/100   0%",
                "[====      ]  42/100  42%",
                "[=         ]  10/100  10%"
            ))
        )

    def test_replace(self) -> None:
        """test ASCIIBar.replace"""
        output = unittest.mock.Mock(wraps=StringIO())
        bar = ASCIIBar(self.FORMAT, max=100, file=output)
        bar.set_progress(60)
        bar.update()
        output.seek(0)
        output.truncate(0)
        output.reset_mock()
        bar.replace("test", end="42")
        output.flush.assert_called()
        self.assertEqual(
            output.getvalue(),
            "\b" * 25 + "test                     42"
        )

    def test_progress(self) -> None:
        """test ASCIIBar.[set_]progress"""
        output = StringIO()
        bar = ASCIIBar(self.FORMAT, max=100, file=output)
        self.assertEqual(bar.progress(), 0)
        self.assertTrue(bar.set_progress(100))
        self.assertEqual(bar.progress(), 100)
        self.assertFalse(bar.set_progress(101))
        self.assertEqual(bar.progress(), 100)

    def test_target(self) -> None:
        """test ASCIIBar.target"""
        self.assertEqual(
            ASCIIBar(self.FORMAT, max=42, file=StringIO()).target(),
            42
        )

    def test_width(self) -> None:
        self.assertEqual(
            ASCIIBar(self.FORMAT, file=StringIO()).width(),
            self.FORMAT.width
        )

    def test_format_progress(self) -> None:
        """test ASCIIBar.format_progress"""
        bar = ASCIIBar(self.FORMAT, 124, file=StringIO())
        output = []
        for i in (29, 30, 124, 0):
            bar.set_progress(i)
            output.append(bar.format_progress())
        self.assertEqual(
            output,
            [" 29/124", " 30/124", "124/124", "  0/124"]
        )

    def test_format_percent(self) -> None:
        """test ASCIIBar.format_percent"""
        bar = ASCIIBar(self.FORMAT, 1000, file=StringIO())
        output = []
        for i in (299, 300, 1000, 0):
            bar.set_progress(i)
            output.append(bar.format_percent())
        self.assertEqual(
            output,
            [" 29%", " 30%", "100%", "  0%"]
        )

    def test_format_bar(self) -> None:
        """test ASCIIBar.format_bar"""
        bar = ASCIIBar(self.FORMAT, file=StringIO())
        output = []
        for i in (29, 30, 100, 0):
            bar.set_progress(i)
            output.append(bar.format_bar())
        self.assertEqual(
            output,
            ["[==        ]", "[===       ]", "[==========]", "[          ]"]
        )


class TestThresholdDecorator(unittest.TestCase):
    """Tests for ThresholdDecorator"""

    def test_eq(self) -> None:
        """test ThresholdDecorator.__eq__"""
        bar = unittest.mock.Mock(spec=Bar)
        decorators = [
            PercentDecorator(bar, 0, 1),
            PercentDecorator(bar, 0, 0),
            PercentDecorator(bar, 1, 1),
            PercentDecorator(unittest.mock.Mock(spec=Bar), 0, 1)
        ]
        for decorator in decorators:
            self.assertEqual(
                [decorator],
                [d for d in decorators if ThresholdDecorator.__eq__(d, decorator)]
            )
        self.assertIs(ThresholdDecorator.__eq__(decorators[0], 42), NotImplemented)

    def test_update(self) -> None:
        """test ThresholdDecorator.update"""
        bar = unittest.mock.Mock(spec=ThresholdDecorator)
        bar.bar = bar
        bar.upper_threshold = 10
        bar.lower_threshold = 5
        bar.progress.configure_mock(side_effect=(5, 10, 0))
        ThresholdDecorator.update(bar)
        bar.update.assert_not_called()
        bar.update_thresholds.assert_not_called()
        ThresholdDecorator.update(bar)
        bar.update.assert_called()
        bar.update_thresholds.assert_called()
        bar.reset_mock()
        ThresholdDecorator.update(bar)
        bar.update.assert_called()
        bar.update_thresholds.assert_called()

    def test_replace(self) -> None:
        """test ThresholdDecorator.replace"""
        bar = unittest.mock.Mock(spec=Bar)
        bar.bar = bar
        ThresholdDecorator.replace(bar, "test", end="42")
        ThresholdDecorator.replace(bar, "test", "42")
        bar.replace.assert_has_calls((unittest.mock.call("test", "42"),) * 2)

    def test_progress(self) -> None:
        """test ThresholdDecorator.[set_]progress"""
        bar = unittest.mock.Mock(spec=Bar)
        bar.progress.configure_mock(side_effect=lambda: 42)
        bar.set_progress.configure_mock(side_effect=(True, False))
        bar.bar = bar
        self.assertEqual(
            ThresholdDecorator.progress(bar),
            42
        )
        self.assertTrue(ThresholdDecorator.set_progress(bar, 42))
        self.assertFalse(ThresholdDecorator.set_progress(bar, 24))
        bar.set_progress.assert_has_calls((
            unittest.mock.call(42),
            unittest.mock.call(24)
        ))

    def test_target(self) -> None:
        """test ThresholdDecorator.target"""
        bar = unittest.mock.Mock(spec=Bar)
        bar.target.configure_mock(side_effect=lambda: 42)
        bar.bar = bar
        self.assertEqual(
            ThresholdDecorator.target(bar),
            42
        )

    def test_width(self) -> None:
        """test ThresholdDecorator.width"""
        bar = unittest.mock.Mock(spec=Bar)
        bar.width.configure_mock(side_effect=lambda: 42)
        bar.bar = bar
        self.assertEqual(
            ThresholdDecorator.width(bar),
            42
        )


class TestPercentDecorator(unittest.TestCase):
    """Tests for PercentDecorator"""

    def test_with_inferred_thresholds(self) -> None:
        """test PercentDecorator.with_inferred_thresholds"""
        bar = ASCIIBar(BarFormat(("[", "]"), (" ", "="), 10), max=1000, file=StringIO())
        decorator = PercentDecorator.with_inferred_thresholds(bar)
        self.assertEqual(decorator.lower_threshold, 0)
        self.assertEqual(decorator.upper_threshold, 10)
        bar.set_progress(494)
        decorator = PercentDecorator.with_inferred_thresholds(bar)
        self.assertEqual(decorator.lower_threshold, 490)
        self.assertEqual(decorator.upper_threshold, 500)

    def test_update_thresholds(self) -> None:
        """test PercentDecorator.update_thresholds"""
        bar = ASCIIBar(BarFormat(("[", "]"), (" ", "="), 10), max=1000, file=StringIO())
        decorator = PercentDecorator(bar, 0, 0)
        decorator.update_thresholds()
        self.assertEqual(decorator.lower_threshold, 0)
        self.assertEqual(decorator.upper_threshold, 10)
        decorator.set_progress(494)
        decorator.update_thresholds()
        self.assertEqual(decorator.lower_threshold, 490)
        self.assertEqual(decorator.upper_threshold, 500)


class TestBarDecorator(unittest.TestCase):
    """Tests for BarDecorator"""

    def test_with_inferred_thresholds(self) -> None:
        """test BarDecorator.test_with_inferred_thresholds"""
        bar = ASCIIBar(BarFormat(("[", "]"), (" ", "="), 10), max=100, file=StringIO())
        decorator = BarDecorator.with_inferred_thresholds(bar)
        self.assertEqual(decorator.lower_threshold, 0)
        self.assertEqual(decorator.upper_threshold, 10)
        bar.set_progress(48)
        decorator = BarDecorator.with_inferred_thresholds(bar)
        self.assertEqual(decorator.lower_threshold, 40)
        self.assertEqual(decorator.upper_threshold, 50)

    def test_update_thresholds(self) -> None:
        """test BarDecorator.update_thresholds"""
        bar = ASCIIBar(BarFormat(("[", "]"), (" ", "="), 10), max=100, file=StringIO())
        decorator = BarDecorator(bar, 0, 0)
        decorator.update_thresholds()
        self.assertEqual(decorator.lower_threshold, 0)
        self.assertEqual(decorator.upper_threshold, 10)
        decorator.set_progress(48)
        decorator.update_thresholds()
        self.assertEqual(decorator.lower_threshold, 40)
        self.assertEqual(decorator.upper_threshold, 50)


class TestBarFormat(unittest.TestCase):
    """Tests for BarFormat"""

    FORMAT = BarFormat(("-[", "]-"), ("  ", "=="), 5)

    def test_init(self) -> None:
        """test barFormat.__init__"""
        with self.assertRaises(ValueError):
            BarFormat(("[", "]"), ("  ", "="), 5)

    def test_eq(self) -> None:
        """test BarFormat.__eq__"""
        formats = [
            self.FORMAT,
            BarFormat(("[", "]"), ("  ", "=="), 5),
            BarFormat(("-[", "]-"), (" ", "="), 5),
            BarFormat(("-[", "]-"), ("  ", "=="), 10),
            BarFormat(("-[", "]-"), ("  ", "=="), 5, format="{bar}"),
            BarFormat(("-[", "]-"), ("  ", "=="), 5, wrapper=lambda i: self.fail())
        ]
        for format in formats:
            self.assertEqual(
                [format],
                [f for f in formats if f == format]
            )
        self.assertNotEqual(self.FORMAT, 42)

    def test_with_optimized_wrapper(self) -> None:
        """test BarFormat.with_optimized_wrapper"""
        formats = list(map(
            lambda f: BarFormat.with_optimized_wrapper(("-[", "]-"), ("  ", "=="), 10, format=f),
            ("x{progress}x", "x{percent}x", "x{bar}x", "x{bar} {percent} {progress}x", "x{percent} {bar}x")
        ))
        output = StringIO()
        bars = (
            ASCIIBar(formats[0], 100, output),
            PercentDecorator(ASCIIBar(formats[1], 100, output), 0, 1),
            BarDecorator(ASCIIBar(formats[2], 100, output), 0, 10),
            ASCIIBar(formats[3], 100, output),
            PercentDecorator(ASCIIBar(formats[4], 100, output), 0, 1)
        )
        for format, bar in zip(formats, bars):
            self.assertEqual(format.bar(100, output), bar)
        with self.assertRaises(ValueError):
            BarFormat.with_optimized_wrapper(("-[", "]-"), ("  ", "=="), 5, format="{0:.}")
        with self.assertRaises(ValueError):
            BarFormat.with_optimized_wrapper(("-[", "]-"), ("  ", "=="), 5, format="42")

    def test_bar(self) -> None:
        """test BarFormat.bar"""
        output = StringIO()
        bar = ASCIIBar(self.FORMAT, max=42, file=output)
        self.assertEqual(
            self.FORMAT.bar(42, output),
            bar
        )
        self.assertIs(
            BarFormat(
                ("-[", "]-"),
                ("  ", "=="),
                5,
                wrapper=lambda b: bar
            ).bar(100, output),
            bar
        )

    def test_generate_bar(self) -> None:
        """test BarFormat.generate_bar"""
        self.assertEqual(self.FORMAT.generate_bar(0.1), "-[          ]-")
        self.assertEqual(self.FORMAT.generate_bar(0.2), "-[==        ]-")
        self.assertEqual(self.FORMAT.generate_bar(1), "-[==========]-")
