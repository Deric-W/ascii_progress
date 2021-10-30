#!/usr/bin/python3

"""Module for creating ascii spinners"""

# Copyright (c) 2020 Eric W.
# SPDX-License-Identifier: MIT

import sys
from typing import ContextManager, Iterator, TextIO, Sequence, TypeVar

__all__ = (
    "SpinnerContext",
    "Spinner"
)

T = TypeVar("T", bound="Spinner")


class SpinnerContext(ContextManager[T]):
    """context manager which handles exceptions while using the spinner"""

    spinner: T

    message: str

    error: str

    __slots__ = ("spinner", "message", "error")

    def __init__(self, spinner: T, message: str, error: str) -> None:
        self.spinner = spinner
        self.message = message
        self.error = error

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SpinnerContext):
            return self.spinner == other.spinner \
                and self.message == other.message \
                and self.error == other.error
        return NotImplemented

    def __enter__(self) -> T:
        return self.spinner

    def __exit__(self, type, value, traceback) -> bool:     # type: ignore
        if type is None:
            self.spinner.replace(self.message, end="\n")
        elif type is KeyboardInterrupt:
            # add 2 \b and 2 spaces to handle additional ^C
            # add 2 additional spaces to make up for missing padding
            self.spinner.replace("\b\b" + self.error, end="    \n")     
        else:
            self.spinner.replace(self.error, end="\n")
        return False    # we dont handle exceptions


class Spinner(Iterator[None]):
    """class for creating a spinning animation"""

    frames: Sequence[str]

    frame: int

    current_padding: int

    file: TextIO

    __slots__ = ("frames", "frame", "current_padding", "file")

    def __init__(self, frames: Sequence[str], file: TextIO = sys.stdout) -> None:
        """init with sequence of frames to display and file to write to"""
        self.frames = frames
        self.frame = 0
        self.current_padding = 0
        self.file = file
        self.file.write(self.current_frame)
        self.file.flush()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Spinner):
            return self.frames == other.frames \
                and self.frame == other.frame \
                and self.current_padding == other.current_padding \
                and self.file is other.file
        return NotImplemented

    def __iter__(self) -> "Spinner":
        return self

    def __next__(self) -> None:
        self.set_progress(self.frame + 1)
        return None

    @classmethod
    def with_padding(cls, frames: Sequence[str], file: TextIO = sys.stdout) -> "Spinner":
        """pad the frames to prevent the cursor from moving"""
        max_size = max(map(len, frames))
        return cls(
            tuple(frame + " " * (max_size - len(frame)) for frame in frames),
            file
        )

    @property
    def current_frame(self) -> str:
        """access current frame of spinner"""
        return self.frames[self.frame]

    @current_frame.setter
    def current_frame(self, frame: str) -> None:
        self.update(self.frames.index(frame))

    def update(self, frame: int) -> None:
        """update spinner"""
        new_frame = self.frames[frame]
        old_size = len(self.current_frame)
        self.reset()  # set position to start of current frame
        self.frame = frame
        self.current_padding = max(old_size - len(new_frame), 0)
        self.file.write(new_frame + " " * self.current_padding)
        self.file.flush()   # ignore line buffering

    def reset(self) -> None:
        """move the cursor to the start of the frame"""
        self.file.write("\b" * (len(self.current_frame) + self.current_padding))

    def set_progress(self, progress: int) -> None:
        """set progress of spinner"""
        self.update(progress % len(self.frames))    # prevent IndexError if progress >= len(frames)

    def replace(self, message: str, end: str = "\n") -> None:
        """replace spinner with message"""
        self.reset()  # set position to start of current frame
        # pad message to fully overwrite old frame and add end
        self.file.write(message + " " * (len(self.current_frame) - len(message)) + end)
        self.file.flush()

    def handle_exceptions(self: T, message: str, error: str) -> SpinnerContext[T]:
        """return a context manager which replaces the spinner with message or error if a exceptions is raised"""
        return SpinnerContext(self, message, error)
