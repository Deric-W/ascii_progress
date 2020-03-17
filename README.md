# ascii-progress
Python module for creating ascii spinners and progress bars

## Content
The module conatains the following:
 - `Spinner`, a class wich is used to create spinners
   - is initialised with a list of frames to cycle through, a message and end to display when the spinner is closed and a file to write to
   - creates an spinner at the current position of the stream and can be used as a context manager and by multiple threads at the same time
   - contains the following methods:
     - `get_frame`, wich returns the frame currently displayed
     - `add_progress`, wich makes the spinner show the next frame (defaults to 1)
     - `set_progress`, wich makes the spinner show a specific frame (defaults to 0)
     - `close`, wich replaces the spinner with the message + end
 - `Bar`, a class wich is used to create progress bars
    - is initialised with a width, max progress, format string wich is can be formated with {bar}, {progress} and {percent}, a message and end to display when the bar is closed, a list of 2 borders with the left as index 0 and the right as index 1, a list of bars with the empthy as index 0 and the full as index 1 and a file to write to
    - creates as loading bar at the current position of the stream and can be used as a context manager, by multiple threads at the same time and as iterator
    - contains the following methods:
      - `_progress`, wich returns the current progress as already formated string
      - `bar`, wich returns the current bar as string
      - `percent`, wich returns the current percentage of the bar as string
      - `add_progress`, wich will increase the progress of the bar (defaults to 1)
      - `set_progress`, wich will set the progress to a specific value (defaults to 0)
      - `close`, wich replaces the bar with the message + end
  - multiple spinner examples as `SPINNER_*`
  - multiple border examples as `BAR_BORDER_*`
  - multiple bar examples as `BAR_BARS_*`
  - a little demo wich is displayed if the module is executed with `python3 -m ascii_progress`

## Install
Drop `ascii_progress.py` somewhere in `sys.path` or use `python3 setup.py install`.

## Problems
Because this module uses only ASCII characters to display output it can be disturbed by the user pressing keys.