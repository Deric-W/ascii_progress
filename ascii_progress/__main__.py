#!/usr/bin/python3
import sys
import time
from .spinner import Spinner
from .bar import BarFormat

# run demo
for frames in (
    "|/-\\",
    ("←↖↑↗→↘↓↙"),
    ("◐◓◑◒"),
    ("(o    )", "( o   )", "(  o  )", "(   o )", "(    o)", "(   o )", "(  o  )", "( o   )"),
    (".oO@*"),
    ("", ".", "..", "..."),
    ("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"),
    (">))'>", "    >))'>", "        >))'>", "        <'((<", "    <'((<", "<'((<")
):
    sys.stdout.write("Working ")
    with Spinner(frames) as spinner:
        for i in range(1, 15):
            spinner.add_progress()
            time.sleep(0.2)

for bar_format in map(
    lambda t: BarFormat(t[0], t[1], 10),
    (
        (("[", "]"), (".", "#")),
        (("|", "|"), (" ", "█")),
        (("[", "]"), (" ", "="))
    )
):
    sys.stdout.write("Working ")
    with bar_format.bar(75) as bar:
        for _ in bar:
            time.sleep(0.02)
