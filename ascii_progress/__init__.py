#!/usr/bin/python3

"""Module for creating ascii spinners and progress bars"""

import sys
import math
from string import Formatter
from dataclasses import dataclass
from typing import Sequence, TextIO, Tuple, Iterator, ContextManager

__version__ = "0.3"
__author__ = "Eric Wolf"
__maintainer__ = "Eric Wolf"
__email__ = "robo-eric@gmx.de"
__contact__ = "https://github.com/Deric-W/ascii-progress"


class Spinner(ContextManager, Iterator[None]):
    """class for creating a spinning animation"""
    def __init__(self, frames: Sequence[str], file: TextIO = sys.stdout) -> None:
        """init with sequence of frames to display and file to write to"""
        self.max_length = max(len(frame) for frame in frames)
        self.frames = tuple(frame + " " * (self.max_length - len(frame)) for frame in frames)
        self.frame = 0
        self.file = file
        self.file.write(self.current_frame)
        self.file.flush()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is KeyboardInterrupt:   # add 2 \b and 2 spaces to handle additional ^C
            self.replace("\b\bKeyboardInterrupt", end="  \n")
        else:
            self.replace("Finished")
        return False    # we dont handle exceptions
    
    def __iter__(self):
        return self
    
    def __next__(self) -> None:
        self.add_progress(1)
        return None
    
    @property
    def current_frame(self) -> str:
        """access current frame of spinner"""
        return self.frames[self.frame]
    
    @current_frame.setter
    def current_frame(self, frame: str) -> None:
        self.frame = self.frames.index(frame)

    def update(self) -> None:
        """update spinner"""
        self.file.write("\b" * self.max_length) # set position to start of current frame
        self.file.write(self.current_frame)
        self.file.flush()   # ignore line buffering  
        
    def add_progress(self, progress: int = 1) -> None:
        """add progress to spinner"""
        self.set_progress(self.frame + progress)

    def set_progress(self, progress: int = 0) -> None:
        """set progress of spinner"""
        self.frame = progress % len(self.frames)    # prevent IndexError if progress >= len(frames)
        self.update()

    def replace(self, message: str, end: str = "\n") -> None:
        """replace spinner with message"""
        self.file.write("\b" * self.max_length) # set position to start of current frame
        self.file.write(message + " " * (self.max_length - len(message)) + end)  # pad message to fully overwrite old frame and add end
        self.file.flush()


@dataclass
class BarFormat:
    """format of a progress bar"""
    borders: Tuple[str, str]
    bars: Tuple[str, str]
    width: int

    def __post_init__(self) -> None:
        if len(self.bars[0]) != len(self.bars[1]):
            raise ValueError("bars not having the same length")

    def generate(self, percent: float) -> str:
        """generate a bar"""
        bars = int(self.width / 100 * percent)
        return self.borders[0] + self.bars[1] * bars + self.bars[0] * (self.width - bars) + self.borders[1]


class BarFormatter(Formatter):
    """formatter for lazy formatting the format of a bar"""
    def __init__(self, bar, format: str) -> None:
        self.bar = bar
        self.format_string = format
    
    def format(self) -> str:
        return self.vformat(self.format_string, tuple(), {})

    def get_value(self, key, args, kwargs) -> str:
        if key == "bar":
            return self.bar.current_bar()
        elif key == "progress":
            return self.bar.current_progress()
        elif key == "percent":
            return self.bar.current_percent()
        else:
            raise KeyError("key not supported")


class Bar(ContextManager, Iterator[None]):
    """class for creating progress bars"""
    def __init__(self, bar_format: BarFormat, max: float = 100, format: str = "{bar} {progress} {percent}", file: TextIO = sys.stdout) -> None:
        """init with format of the bar, progress at 100%, format of the displayed bar and file"""
        self.bar_format = bar_format
        self.max = max
        self.progress = 0.0
        self.formatter = BarFormatter(self, format)
        self.file = file
        self.file.write(self.formatter.format())
        self.file.flush()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is KeyboardInterrupt:   # handle ^C
            self.replace("\b\bKeyboardInterrupt", end="  \n")
        else:
            self.replace("Finished")
        return False    # we dont handle exceptions

    def __iter__(self):
        return self

    def __next__(self) -> None:
        if self.progress >= self.max:   # reached max iterations
            raise StopIteration
        else:
            self.add_progress(1)
            return None
    
    def update(self) -> None:
        """update bar"""
        bar = self.formatter.format()
        self.file.write("\b" * len(bar))
        self.file.write(bar)
        self.file.flush()
    
    def current_progress(self) -> str:
        """generate progress"""
        return "{0: >{max_length}.0F}/{1: >{max_length}.0F}".format(self.progress, self.max, max_length=int(math.log10(self.max)) + 1)

    def current_bar(self) -> str:
        """generate bar"""
        return self.bar_format.generate(self.progress / (self.max / 100))

    def current_percent(self) -> str:
        """generate percent"""
        return "{0: >5.1f}%".format(self.progress / (self.max / 100))

    def add_progress(self, progress: float = 1) -> None:
        """add progress to bar"""
        self.progress += progress
        self.update()

    def set_progress(self, progress: float = 0) -> None:
        """set progress of bar"""
        self.progress = progress       
        self.update()

    def replace(self, message: str, end: str = "\n") -> None:
        """replace bar with message"""
        bar_length = len(self.formatter.format())
        self.file.write("\b" * bar_length)
        self.file.write(message + " " * (bar_length - len(message)) + end) # pad message to fully overwrite bar
