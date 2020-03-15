#!/usr/bin/python3

"""Module for creating ascii spinners and progress bars"""

__version__ = "0.1"
__author__ = "Eric Wolf"
__maintainer__ = "Eric Wolf"
__email__ = "robo-eric@gmx.de"
__contact__ = "https://github.com/Deric-W/ascii-progress"

import sys
from threading import Lock

# Spinners
SPINNER_LINES = ("|", "/", "-", "\\")
SPINNER_DOTS = ("", ".", "..", "...")
SPINNER_DOTS_SQUARE = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
SPINNER_ARROWS = ("←", "↖", "↑", "↗", "→", "↘", "↓", "↙")
SPINNER_BALLONS = (".", "o", "O", "@", "*")
SPINNER_BALL = ("◐", "◓", "◑", "◒")
SPINNER_BOUNCING_BALL = ("(o    )", "( o   )", "(  o  )", "(   o )", "(    o)", "(   o )", "(  o  )", "( o   )")
SPINNER_FISH = (">))'>", "    >))'>", "        >))'>", "        <'((<", "    <'((<", "<'((<")

# Bars
BAR_BORDERS_APT = ("[", "]")
BAR_BARS_APT = (".", "#")
BAR_BORDERS_PIP = ("|", "|")
BAR_BARS_PIP = (" ", "█")
BAR_BORDERS_CUSTOM = BAR_BORDERS_APT
BAR_BARS_CUSTOM = (" ", "=")
# many more possible!


class Spinner:
    """class for creating a spinning animation"""
    def __init__(self, frames=SPINNER_LINES, message="", end="\n", file=sys.stdout):
        """init with iterable of frames to display, a message to replace the spinner with at .close() and file to write to"""
        self.lock = Lock() # for threading support
        self.frames = frames
        self.max_length = len(max(frames, key=len))  # to prevent only partial overwrite of old frames
        self.message = message  # message to replace spinner with at .close()
        self.end = end  # end of message
        self.file = file
        self.frame = 0
        self.file.write(self.get_frame() + " " * (self.max_length - len(self.get_frame())))  # pad frame to fully overwrite old one
        self.file.flush()

    def __enter__(self):    # can be used as context manager
        return self

    def __exit__(self, type, value, traceback):
        if type is KeyboardInterrupt:   # prevent the ^C from messing up the message
            self.close(interrupted=True)
        else:
            self.close()
        return False    # we dont handle exceptions

    def _update(self):
        """update spinner, not thread safe"""
        self.file.write("\b" * self.max_length) # set position to start of current frame
        self.file.write(self.get_frame() + " " * (self.max_length - len(self.get_frame())))  # pad frame to fully overwrite old one
        self.file.flush()   # ignore line buffering  

    def get_frame(self):
        """get current frame"""
        return self.frames[self.frame]
        
    def add_progress(self, progress=1):
        """add progress to spinner"""
        with self.lock:
            self.frame = (self.frame + progress) % len(self.frames) # prevent IndexError if progress >= len(frames)  
            self._update()  

    def set_progress(self, progress=0):
        """set progress of spinner"""
        with self.lock:
            self.frame = progress % len(self.frames)    # prevent IndexError if progress >= len(frames)
            self._update()

    def close(self, interrupted=False):
        """replace spinner with message"""
        with self.lock:
            self.file.write("\b" * self.max_length) # set position to start of current frame
            if interrupted:   # add 2 \b and 2 spaces to handle additional ^C
                self.file.write("\b\bKeyboardInterrupt" + " " * (self.max_length - len("KeyboardInterrupt")) + "  " + self.end)  # pad error message to fully overwrite old frame and add end
            else:
                self.file.write(self.message + " " * (self.max_length - len(self.message)) + self.end)  # pad message to fully overwrite old frame and add end
            self.file.flush()


class Bar:
    """class for creating progress bars"""
    def __init__(self, width, max=100, format="{bar} {percent}", message="", end="\n", borders=BAR_BORDERS_APT, bars=BAR_BARS_APT, file=sys.stdout):
        """init with width on display, progress at 100%, format of the bar, message + end, borders, bars (same length) and file"""
        if len(bars[0]) != len(bars[1]):    # prevent size changing bar
            raise ValueError("bars do not have same length")
        self.lock = Lock()  # threading support
        self.width = width
        self.max = max
        self.progress = 0
        self.format = format
        self.message = message
        self.end = end
        self.borders = borders
        self.bars = bars
        self.file = file
        self.file.write(self.format.format(bar=self.bar(), percent=self.percent()))
        self.file.flush()

    def __enter__(self):    # can be used as context manger
        return self

    def __exit__(self, type, value, traceback):
        if type is KeyboardInterrupt:   # handle ^C
            self.close(interrupted=True)
        else:
            self.close()
        return False    # we dont handle exceptions

    def __iter__(self): # can be used as iterator
        return self

    def __next__(self):
        if self.progress == self.max:   # reached max iterations
            raise StopIteration
        else:
            self.add_progress(1)
            return self.progress
    
    def _update(self):
        """update bar, not thread safe"""
        format = self.format.format(bar=self.bar(), percent=self.percent())
        self.file.write("\b" * len(format))
        self.file.write(format)
        self.file.flush()

    def bar(self):
        """generate bar"""
        percent = int(self.progress / (self.max / 100))
        bars = int(self.width / 100 * percent)
        return self.borders[0] + self.bars[1] * bars + self.bars[0] * (self.width - bars) + self.borders[1]

    def percent(self):
        """generate percent"""
        percent = int(self.progress / (self.max / 100))
        if percent < 10:    #add 2 spaces
            return "  {}%".format(percent)
        elif percent < 100: # add one space
            return " {}%".format(percent)
        else:   # add no spaces
            return "{}%".format(percent)

    def add_progress(self, progress=1):
        """add progress to bar"""
        with self.lock:
            self.progress += progress
            if self.progress > self.max:    # prevent overflow
                self.progress = self.max
            self._update()

    def set_progress(self, progress=0):
        """set progress of bar"""
        with self.lock:
            self.progress = progress
            if self.progress > self.max:    # prevent overflow
                self.progress = self.max        
            self._update()

    def close(self, interrupted=False):
        """replace bar with message"""
        with self.lock:
            format = self.format.format(bar=self.bar(), percent=self.percent())
            self.file.write("\b" * len(format))
            if interrupted: # same procedure like Spinner
                self.file.write("\b\bKeyboardInterrupt" + " " * (len(format) - len("KeyboardInterrupt")) + "  " + self.end)
            else:
                self.file.write(self.message + " " * (len(format) - len(self.message)) + self.end) # pad message to fully overwrite bar


if __name__ == "__main__":  # run demo
    import time

    for frames in (SPINNER_LINES, SPINNER_ARROWS, SPINNER_BALL, SPINNER_BOUNCING_BALL, SPINNER_BALLONS, SPINNER_DOTS, SPINNER_DOTS_SQUARE, SPINNER_FISH):
        sys.stdout.write("Working ")
        with Spinner(frames, "Done") as spinner:
            for i in range(1, 10):
                spinner.add_progress()
                time.sleep(0.2)
    
    for variant in ((BAR_BORDERS_APT, BAR_BARS_APT), (BAR_BORDERS_PIP, BAR_BARS_PIP), (BAR_BORDERS_CUSTOM, BAR_BARS_CUSTOM), (("-[", "]-"), ("--", "**"))):
        sys.stdout.write("Working ")
        with Bar(10, message="Done", borders=variant[0], bars=variant[1]) as bar:
            for i in range(1,110):  # prove resistance against overflows
                bar.add_progress(1)
                time.sleep(0.02)
