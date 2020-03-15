#!/usr/bin/python3

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
    def __init__(self, frames=SPINNER_LINES, message="", file=sys.stdout):
        """init with iterable of frames to display, a message to replace the spinner with at .close() and file to write to"""
        self.lock = Lock() # for threading support
        self.frames = frames
        self.max_length = len(max(frames, key=len))  # to prevent only partial overwrite of old frames
        self.message = message  # message to replace spinner with at .close()
        self.file = file
        self.frame = 0
        self.file.write(self.get_frame() + " " * (self.max_length - len(self.get_frame())))  # pad frame to fully overwrite old one
        self.file.flush()

    def __enter__(self):
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
                self.file.write("\b\bKeyboardInterrupt" + " " * (self.max_length - len("KeyboardInterrupt")) + "  \n")  # pad error message to fully overwrite old frame and add newline
            else:
                self.file.write(self.message + " " * (self.max_length - len(self.message)) + "\n")  # pad message to fully overwrite old frame and add newline
            self.file.flush()


class Bar:
    def __init__(self, width, max=100, borders=BAR_BORDERS_APT, bars=BAR_BARS_APT, file=sys.stdout):
        self.lock = Lock()
        self.max = max
        self.borders = borders
        if len(bars[0]) > len(bars[1]):                                     # make bars have the same length
            self.bars = bars[0], bars[1] + " " * (len(bars[0]) - len(bars[1]))
        elif len(bars[0]) < len(bars[1]):
            self.bars = bars[0] + " " * (len(bars[1]) - len(bars[0])), bars[1]
        else:
            self.bars = bars
        self.width = width
        self.file = file
        self.state = 0
        self.closed = False
        self.file.write(borders[0] + bars[0] * width + borders[1])
        self.file.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.state == self.max:                                       # reached max iterations
            raise StopIteration
        else:
            self.add_progress(amount=1)
            return self.state

    def __check_closed(self):
        if self.closed:
            raise RuntimeError("Bar closed")

    def __update_bar(self):
        accuracy = self.max / self.width
        bar_count = int(self.state / accuracy)
        full_bar = self.bars[1] * bar_count
        empty_bar = self.bars[0] * (self.width - bar_count)
        length = self.width * len(self.bars[0]) + len(self.borders[0]) + len(self.borders[1])
        self.file.write("\b" * length)
        self.file.write(self.borders[0] + full_bar + empty_bar + self.borders[1])
        self.file.flush()

    def get_percentage(self):
        self.__check_closed()
        return self.state / (self.max / 100)

    def get_progress(self):
        self.__check_closed()
        return self.state        

    def add_progress(self, amount=1):
        self.__check_closed()
        with self.lock:
            self.state += amount
            if self.state > self.max:                                  # prevent overflow
                self.state = self.max
            self.__update_bar()

    def set_progress(self, state=0):
        self.__check_closed()
        with self.lock:
           self.state = state
           if self.state > self.max:
               self.state = self.max
           self.__update_bar()

    def close(self, message="", end="\n"):                              # the same purpose as Spinner.close
        self.__check_closed()
        with self.lock:
            self.closed = True
            length = self.width * len(self.bars[0]) + len(self.borders[0]) + len(self.borders[1])
            padding = length - len(message)
            self.file.write("\b" * length)
            self.file.write(message + " " * padding + end)
            self.file.flush()


if __name__ == "__main__":  # run demo
    import time

    for frames in (SPINNER_LINES, SPINNER_ARROWS, SPINNER_BALL, SPINNER_BOUNCING_BALL, SPINNER_BALLONS, SPINNER_DOTS, SPINNER_DOTS_SQUARE, SPINNER_FISH):
        sys.stdout.write("Working ")
        with Spinner(frames, "Done") as spinner:
            for i in range(1, 10):
                spinner.add_progress()
                time.sleep(0.2)

    sys.stdout.write("Working ")
    test = Bar(10)
    for i in range(0, 110):                         # no overflows
        test.add_progress()
        time.sleep(0.05)
    test.close("Done")

    sys.stdout.write("Working ")
    test = Bar(10, borders=BAR_BORDERS_PIP, bars=BAR_BARS_PIP)
    for i in range(0, 110):                         # no overflows
        test.add_progress()
        time.sleep(0.05)
    test.close("Done")

    sys.stdout.write("Working ")
    test = Bar(10, borders=BAR_BORDERS_CUSTOM, bars=BAR_BARS_CUSTOM)
    for i in range(0, 110):                         # no overflows
        test.add_progress()
        time.sleep(0.05)
    test.close("Done")

    sys.stdout.write("Working ")
    test = Bar(10, borders=("-[", "]-"), bars=("--", "**"))
    for i in range(0, 110):                         # no overflows
        test.add_progress()
        time.sleep(0.05)
    test.close("Done")
