# ascii-progress
Python module for creating ascii spinners and progress bars

## Content
The module contains the following:
 - `Spinner`, a class which is used to create spinners
   - is initialised with a list of frames to cycle through, and a file to write to
   - creates an spinner at the current position of the stream and can be used as a context manager
   - contains the following methods:
     - `add_progress`, which makes the spinner show the next frame (defaults to 1)
     - `set_progress`, which makes the spinner show a specific frame (defaults to 0)
     - `replace`, which replaces the spinner with the message + end
   - contains the `current_frame` property to get/set the current frame as a str
 - `BarFormat`, a class which stores the format information of a progress bar
   - is initialised with a tuple containing the left and right bar borders, a tuple containing a empty and a filled bar part and the width of the progress bar
 - `Bar`, a class which is used to create progress bars
    - is initialised with a BarFormat, max progress, format string which is can be formated with {bar}, {progress} and {percent} and a file to write to
    - creates as progress bar at the current position of the stream and can be used as a context manager and as iterator
    - contains the following methods:
      - `current_progress`, which returns the current progress as a already formatted string
      - `current_bar`, which returns the current bar as string
      - `current_percent`, which returns the current percentage of the bar as string
      - `add_progress`, which will increase the progress (defaults to 1)
      - `set_progress`, which will set the progress to a specific value (defaults to 0)
      - `replace`, which replaces the bar with the message + end
  - multiple examples in the `examples` submodule
  - a little demo which is displayed if the module is executed with `python3 -m ascii_progress`

## Install
Drop `ascii_progress.py` somewhere in `sys.path` or use `python3 setup.py install`.

## Problems
 - because this module uses only ASCII characters to display output it can be disturbed by the user pressing keys
 - Spinner and Bar update every time the progress in increased, even if it is not necessary which reduces performance