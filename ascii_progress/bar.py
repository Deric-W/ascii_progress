#!/usr/bin/python3

"""Module for creating ascii progress bars"""

# Copyright (c) 2020 Eric W.
# SPDX-License-Identifier: MIT

import sys
import math
from abc import abstractmethod
from string import Formatter
from typing import Callable, Sequence, TextIO, Tuple, Iterator, ContextManager, Mapping, Any, Union

__all__ = (
    "LazyFormatter",
    "LAZY_FORMATTER",
    "Bar",
    "ThresholdDecorator",
    "PercentDecorator",
    "BarDecorator",
    "BarFormat"
)


class LazyFormatter(Formatter):
    """formatter which expects functions as arguments"""

    __slots__ = ()

    def get_value(self, key: Union[int, str], args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
        """retrieve a given field value"""
        if isinstance(key, str):
            return kwargs[key]()
        return args[key]()


LAZY_FORMATTER = LazyFormatter()


class Bar(ContextManager["Bar"], Iterator[None]):
    """abstract base class for progress bars"""

    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Bar):
            return self.progress() == other.progress() \
                and self.target() == other.target() \
                and self.width() == other.width()
        return NotImplemented

    def __enter__(self) -> "Bar":
        return self

    def __exit__(self, type, value, traceback) -> bool:     # type: ignore
        if type is KeyboardInterrupt:   # handle ^C
            self.replace("\b\bKeyboardInterrupt", end="  \n")
        else:
            self.replace("Finished")
        return False    # we dont handle exceptions

    def __iter__(self) -> "Bar":
        return self

    def __next__(self) -> None:
        if not self.set_progress(self.progress() + 1):
            raise StopIteration
        self.update()

    @abstractmethod
    def update(self) -> None:
        """redraw bar"""
        raise NotImplementedError

    @abstractmethod
    def replace(self, message: str, end: str = "\n") -> None:
        """replace the bar with a message and end"""
        raise NotImplementedError

    @abstractmethod
    def progress(self) -> int:
        """return the current progress of the bar"""
        raise NotImplementedError

    @abstractmethod
    def set_progress(self, progress: int) -> bool:
        """set the progress if <= target and return if it was successfull"""
        raise NotImplementedError

    @abstractmethod
    def target(self) -> int:
        """return the progress at 100%"""
        raise NotImplementedError

    @abstractmethod
    def width(self) -> int:
        """return the size of the bar"""
        raise NotImplementedError

    def ratio(self) -> float:
        """return the ration progress / target"""
        return self.progress() / self.target()


class ASCIIBar(Bar):
    """ASCII progress bar"""

    bar_format: "BarFormat"

    current_progress: int

    max: int

    file: TextIO

    __slots__ = ("bar_format", "current_progress", "max", "file")

    def __init__(self, bar_format: "BarFormat", max: int = 100, file: TextIO = sys.stdout) -> None:
        """init with format of the bar, progress at 100%, format of the displayed bar and file"""
        self.bar_format = bar_format
        self.max = max
        self.current_progress = 0
        self.file = file
        self.file.write(
            LAZY_FORMATTER.format(
                bar_format.format,
                bar=self.format_bar,
                progress=self.format_progress,
                percent=self.format_percent
            )
        )
        self.file.flush()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ASCIIBar):
            return self.bar_format == other.bar_format \
                and self.current_progress == other.current_progress \
                and self.max == other.max \
                and self.file is other.file
        return NotImplemented

    def update(self) -> None:
        """update bar"""
        bar = LAZY_FORMATTER.format(
            self.bar_format.format,
            bar=self.format_bar,
            progress=self.format_progress,
            percent=self.format_percent
        )
        self.file.write("\b" * len(bar))
        self.file.write(bar)
        self.file.flush()

    def replace(self, message: str, end: str = "\n") -> None:
        """replace bar with message"""
        bar_length = len(
            LAZY_FORMATTER.format(
                self.bar_format.format,
                bar=self.format_bar,
                progress=self.format_progress,
                percent=self.format_percent
            )
        )
        self.file.write("\b" * bar_length)
        self.file.write(message + " " * (bar_length - len(message)) + end)  # pad message to fully overwrite bar
        self.file.flush()

    def progress(self) -> int:
        """return the current progress of the bar"""
        return self.current_progress

    def set_progress(self, progress: int) -> bool:
        """set the progress if <= target and return if it was successfull"""
        if 0 <= progress <= self.target():
            self.current_progress = progress
            return True
        return False

    def target(self) -> int:
        """return the progress at 100%"""
        return self.max

    def width(self) -> int:
        """return the size of the bar"""
        return self.bar_format.width

    def format_bar(self) -> str:
        """generate a string repersentation of the current bar"""
        return self.bar_format.generate_bar(self.ratio())

    def format_progress(self) -> str:
        """generate a string representation of the current progress"""
        target = self.target()
        max_length = int(math.log10(target)) + 1
        return "{0: >{2}.0F}/{1}".format(self.progress(), target, max_length)

    def format_percent(self) -> str:
        """generate a string representation of the current progress in percent"""
        return "{0: >3d}%".format(math.floor(self.ratio() * 100))


class ThresholdDecorator(Bar):
    """decorator which only updates when exceeding thresholds"""
    bar: Bar

    lower_threshold: int

    upper_threshold: int

    __slots__ = ("bar", "lower_threshold", "upper_threshold")

    def __init__(self, bar: Bar, lower_threshold: int, upper_threshold: int) -> None:
        self.bar = bar
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ThresholdDecorator):
            return self.bar == other.bar \
                and self.lower_threshold == other.lower_threshold \
                and self.upper_threshold == other.upper_threshold
        return NotImplemented

    @abstractmethod
    def update_thresholds(self) -> None:
        """update lower and upper thresholds"""
        raise NotImplementedError

    def update(self) -> None:
        """redraw bar"""
        if not self.lower_threshold <= self.bar.progress() < self.upper_threshold:
            self.bar.update()
            self.update_thresholds()

    def replace(self, message: str, end: str = "\n") -> None:
        """replace the bar with a message and end"""
        self.bar.replace(message, end)

    def progress(self) -> int:
        """return the current progress of the bar"""
        return self.bar.progress()

    def set_progress(self, progress: int) -> bool:
        """set the progress if <= target and return if it was successfull"""
        return self.bar.set_progress(progress)

    def target(self) -> int:
        """return the progress at 100%"""
        return self.bar.target()

    def width(self) -> int:
        """return the full size of the bar"""
        return self.bar.width()


def calculate_thresholds(bar: Bar, segments: int) -> Tuple[int, int]:
    """calculate the last and next segment borders for the current progress"""
    segment = math.floor(bar.ratio() * segments)
    target = bar.target()
    return (
        math.floor(segment / segments * target),
        math.ceil((segment + 1) / segments * target)
    )


class PercentDecorator(ThresholdDecorator):
    """decorator which only updates on percent changes"""

    __slots__ = ()

    @classmethod
    def with_inferred_thresholds(cls, bar: Bar) -> "PercentDecorator":
        """create an instance with inferred thresholds"""
        lower_threshold, upper_threshold = calculate_thresholds(bar, 100)
        return cls(
            bar,
            lower_threshold,
            upper_threshold,
        )

    def update_thresholds(self) -> None:
        """update lower and upper thresholds"""
        self.lower_threshold, self.upper_threshold = calculate_thresholds(self.bar, 100)


class BarDecorator(ThresholdDecorator):
    """decorator which only updates on bar changes"""

    __slots__ = ()

    @classmethod
    def with_inferred_thresholds(cls, bar: Bar) -> "BarDecorator":
        """create an instance with inferred thresholds"""
        lower_threshold, upper_threshold = calculate_thresholds(bar, bar.width())
        return cls(
            bar,
            lower_threshold,
            upper_threshold,
        )

    def update_thresholds(self) -> None:
        """update lower and upper thresholds"""
        self.lower_threshold, self.upper_threshold = calculate_thresholds(self.bar, self.bar.width())


class BarFormat:
    """format of a progress bar"""
    borders: Tuple[str, str]

    states: Tuple[str, str]

    width: int

    format: str

    wrapper: Callable[[Bar], Bar]

    __slots__ = ("borders", "states", "width", "format", "wrapper")

    def __init__(self, borders: Tuple[str, str], states: Tuple[str, str], width: int, format: str = "{bar} {progress} {percent}", wrapper: Callable[[Bar], Bar] = lambda b: b) -> None:
        if len(states[0]) != len(states[1]):
            raise ValueError("bar states do not have the same length")
        self.borders = borders
        self.states = states
        self.width = width
        self.format = format
        self.wrapper = wrapper  # type: ignore

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BarFormat):
            return self.borders == other.borders \
                and self.states == other.states \
                and self.width == other.width \
                and self.format == other.format \
                and self.wrapper is other.wrapper   # type:ignore
        return NotImplemented

    @classmethod
    def with_optimized_wrapper(cls, borders: Tuple[str, str], states: Tuple[str, str], width: int, format: str = "{bar} {progress} {percent}") -> "BarFormat":
        """infer bar update optimizations from the format string"""
        variables = {v for _, v, _, _ in LAZY_FORMATTER.parse(format) if v is not None}
        if "progress" in variables:     # changing the bar or percent will always change progress
            wrapper = lambda b: b
        elif "percent" in variables:    # changing the bar will always change percent
            wrapper = lambda b: PercentDecorator(b, 0, math.ceil(b.target() / 100))
        elif "bar" in variables:        # since nothing always changes the bar it is checked for last
            wrapper = lambda b: BarDecorator(b, 0, math.ceil(b.target() / b.width()))
        else:
            raise ValueError("format string is static or contains invalid variables")
        return cls(
            borders,
            states,
            width,
            format,
            wrapper
        )

    def generate_bar(self, ratio: float) -> str:
        """generate a bar representing the ratio progress / target"""
        size = math.floor(self.width * ratio)
        return "".join((
            self.borders[0],
            self.states[1] * size,
            self.states[0] * (self.width - size),
            self.borders[1]
        ))

    def bar(self, target: int, file: TextIO = sys.stdout) -> Bar:
        """create a bar object"""
        return self.wrapper(ASCIIBar(self, target, file))   # type: ignore
