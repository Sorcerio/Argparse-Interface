# ArgUI

![ArgUI's Logo](https://github.com/Sorcerio/Argparse-Interface/blob/master/assets/ArgUILogo_transparent.png?raw=true)

An automatic, terminal based interactive interface for any Python 3 `argparse` command line with keyboard and mouse support.

- [ArgUI](#argui)
  - [See It in Action](#see-it-in-action)
  - [Usage](#usage)
    - [Install as a Dependency](#install-as-a-dependency)
    - [Setup Your Argparse](#setup-your-argparse)
    - [Run Your Program](#run-your-program)
    - [Navigation](#navigation)
  - [Development Setup](#development-setup)

---

## See It in Action

![Demo of the features in ArgUI](https://github.com/Sorcerio/Argparse-Interface/blob/master/assets/ArgUIDemo_small.gif?raw=true)

Get a feel for the features of ArgUI using the [Demo.py](./argui/Demo.py) code included in this project.

## Usage

### Install as a Dependency

The ArgUI package is [available on PyPi](https://pypi.org/project/Argparse-Interface/).

It can be installed by calling: `pip install argparse-interface`

### Setup Your Argparse

ArgUI supports wrapping any implementation of the Python 3 `argparse` native library.
This will all you to use both standard terminal and interface modes to interact with your program.

```python
# Import
import argparse
import argui

# Setup your ArgumentParser normally
parser = argparse.ArgumentParser(prog="Demo")

# `add_argument`, `add_argument_group`, etc...

# Wrap your parser
interface = argui.Wrapper(parser)

# Get arguments
args: argparse.Namespace = interface.parseArgs()

# `args` is the same as if you had called `parser.parse_args()`
```

See [Demo.py](./argui/Demo.py) for more information.

### Run Your Program

Your program can now be run in both CLI and GUI modes.

To run in CLI mode, simply use your script as normal like `python foo.py -h`.

To run in GUI mode, provide only the `--gui` (by default) argument like `python foo.py --gui`.

### Navigation

Mouse navigation of the GUI is possible in _most_ terminals.

There are known issues with the VSCode terminal on Windows 10 and some others.
However, Mouse navigation does work in Powershell when opened on its own.

Keyboard navigation is always available using `Tab`, `Arrow Keys`, and `Enter`.
But make note that if you are using a terminal within another program (like VSCode), that some more advanced keyboard commands (like `CTRL+S`) may be captured by the container program and not sent to the GUI.

## Development Setup

1. Clone this repo and enter the directory with a terminal.
1. Setup a Python Env: `python -m venv .venv --prompt "argUI"`
1. Enter the Python Env.
1. Install requirements: `pip install -r requirements.txt`
