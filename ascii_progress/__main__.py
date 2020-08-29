#!/usr/bin/python3
import sys
import time
from . import Spinner, Bar, BarFormat
from .examples import *

# run demo
for frames in (SPINNER_LINES, SPINNER_ARROWS, SPINNER_BALL, SPINNER_BOUNCING_BALL, SPINNER_BALLONS, SPINNER_DOTS, SPINNER_DOTS_SQUARE, SPINNER_FISH):
    sys.stdout.write("Working ")
    spinner = Spinner(frames)
    try:
        for i in range(1, 10):
            spinner.add_progress()
            time.sleep(0.2)
    except KeyboardInterrupt:
        spinner.replace("\b\bKeyboardInterrupt", end="  \n\n")
    except Exception:
        spinner.replace("Failed")
    else:
        spinner.replace("Done")
    
for variant in ((BAR_BORDERS_APT, BAR_BARS_APT), (BAR_BORDERS_PIP, BAR_BARS_PIP), (BAR_BORDERS_CUSTOM, BAR_BARS_CUSTOM), (("-[", "]-"), ("--", "**"))):
    sys.stdout.write("Working ")
    bar = Bar(BarFormat(variant[0], variant[1], 10), 100)
    try:
        for _ in bar:
            time.sleep(0.02)
    except KeyboardInterrupt:
        bar.replace("\b\bKeyboardInterrupt", end="  \n\n")
    except Exception:
        bar.replace("Failed")
    else:
        bar.replace("Done")
        