# ascii-progress
Python module for creating ascii spinners and progress bars

## Content
The module contains the following:
 - `Spinner`, a class which is used to create spinners
   - is initialised with a list of frames to cycle through, and a file to write to
   - creates an spinner at the current position of the stream and can be used as a context manager and iterator
   - contains the following (class)methods:
     - `with_padding`, which creates a spinner with padded frames to prevent cursor movement
     - `set_progress`, which makes the spinner show a specific frame
     - `replace`, which replaces the spinner with the message + end
   - contains the `current_frame` property to get/set the current frame as a str
 - `BarFormat`, a class which stores the format information of a progress bar
   - is initialised with a tuple containing the left and right bar borders, a tuple containing a empty and a filled bar part, the width of the progress bar and an optional format string specifying the bar layout
   - contains the following (class)methods:
     - `with_optimized_wrapper`, which creates an instance which wrapps created bar objects to prevent unnecessary updates
     - `bar`, which takes the progress of the bar at 100% and a text stream to write to and returns a `Bar` instance
 - `Bar`, an abstract base class for all progress bars and their wrappers
    - instances are obtained by calling `BarFormat.bar`
    - creates as progress bar at the current position of the stream and can be used as a context manager and iterator
    - contains the following methods:
      - `progress`, which returns the current progress
      - `target`, which returns the progress at 100%
      - `current_percent`, which returns the current percentage of the bar as string
      - `update`, which redraws the bar
      - `width`, which returns the number of bar segments
      - `replace`, which replaces the bar with a message + end
  - a little demo with multiple examples which is displayed if the module is executed with `python3 -m ascii_progress`

## Install
Build a wheel with `python3 setup.py bdist_wheel` and install it with pip or use `python3 setup.py install`.

## Problems
 - because this module uses only ASCII characters to display output it can be disturbed by the user pressing keys