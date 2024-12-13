# Argparse Interface

An automatic, terminal based interactive interface for any Python 3 `argparse` command line with keyboard and mouse support.

- [Argparse Interface](#argparse-interface)
  - [Install](#install)
  - [Usage](#usage)
    - [Setup Your Argparse](#setup-your-argparse)
    - [Use the Command Line](#use-the-command-line)
    - [Navigation](#navigation)
  - [Development Setup](#development-setup)

---

## Install

1. Clone this repo to the desired location.
1. Access this directory with your desired environment.
1. Install this repo as a package: `pip install -e .`

A PyPi release may come in the future.

## Usage

### Setup Your Argparse

```python
# Import
import argparse
import argui

# Setup your ArgumentParser normally
parser = argparse.ArgumentParser(prog="Demo")

# `add_argument`, etc...

# Wrap your parser
interface = argui.Wrapper(parser)

# Get arguments in dict format
args = interface.parseArgs()

# Update references to use `args["<key>"]` instead of `args.<key>`
```

### Use the Command Line

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

1. Setup a Python Env: `python -m venv .venv --prompt "argUI"`
1. Enter the Python Env.
1. Install requirements: `pip install -r requirements.txt`
