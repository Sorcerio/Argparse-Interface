# Argparse Interface: Demo
# Demo of the `argparse` interface.

# MARK: Imports
import argparse
import logging
from pprint import pprint

from .Wrapper import Wrapper

# MARK: Functions
def demoCli():
    """
    Runs a demonstration of the `argparse` interface with the Argparse Interface attached.
    """
    # Create the parser
    parser = argparse.ArgumentParser(
        prog="Argparse Interface Test",
        description="A demonstration of argparse interface.",
        epilog="This is the epilog of the demonstration."
    )

    # Add arguments
    parser.add_argument("magicNumber", metavar="NUM", type=int, help="A required int argument")

    parser.add_argument("-s", "--string", type=str, help="A string argument")
    parser.add_argument("-i", "--integer", type=int, help="An integer argument", default=32)
    parser.add_argument("-f", "--float", type=float, help="A float argument")
    parser.add_argument("-bt", "--boolTrue", action="store_true", help="A boolean argument")
    parser.add_argument("-bf", "--boolFalse", action="store_false", help="A boolean argument")
    parser.add_argument("-c", "--choice", type=int, choices=[1, 2, 3], help="A choice argument")
    parser.add_argument("-l", "--list", nargs="+", help="A list argument")

    subparsers = parser.add_subparsers(dest="command", help="A Subcommand")

    foo_parser = subparsers.add_parser("foo")
    foo_parser.add_argument("-x", type=int, default=1)

    bar_parser = subparsers.add_parser("bar")
    bar_parser.add_argument("y", type=float)

    third_parser = subparsers.add_parser("third")
    third_parser.add_argument("-b", action="store_true", help="A boolean argument")

    # Prepare the interface
    interface = Wrapper(
        parser,
        logLevel=logging.DEBUG
    )
    args = interface.parseArgs()

    # Make it pretty
    if args is not None:
        print("Parsed arguments:\n")
        pprint(vars(args))
    else:
        print(f"No arguments parsed:\n{args}")