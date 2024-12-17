# Argparse Interface: Demo
# Demo of the `argparse` interface.

# MARK: Imports
import argparse
import logging
from pprint import pprint

from .Wrapper import Wrapper

# MARK: Functions
def getDemoArgParser() -> argparse.ArgumentParser:
    # Create the parser
    parser = argparse.ArgumentParser(
        prog="Argparse Interface Test",
        description="A demonstration of argparse interface.",
        epilog="This is the epilog of the demonstration."
    )

    # Implicitly required arguments
    parser.add_argument("magicNumber", metavar="NUM", type=int, help="A required int argument")

    # Optional root level arguments
    parser.add_argument("-s", "--string", type=str, help="A string argument")
    parser.add_argument("-i", "--integer", type=int, help="An integer argument", default=32)
    parser.add_argument("-f", "--float", type=float, help="A float argument")
    parser.add_argument("-bt", "--boolTrue", action="store_true", help="A boolean argument")
    parser.add_argument("-bf", "--boolFalse", action="store_false", help="A boolean argument", required=True)
    parser.add_argument("-c", "--choice", type=int, choices=[1, 2, 3], help="A choice argument")
    parser.add_argument("-sz", "--size", help="A specific number of nargs", metavar=("WIDTH", "HEIGHT"), nargs=2)
    parser.add_argument("-a", "--area", help="A specific number of nargs with a default", metavar=("WIDTH", "HEIGHT", "LENGTH"), default=[10, 12, 15], nargs=3)
    parser.add_argument("-l", "--list", nargs="+", help="A list argument")
    parser.add_argument("-ld", "--defaultList", nargs="+", default=[69, 420, 1337], type=int, help="A list argument")

    # Regular argument groups
    group1 = parser.add_argument_group(title="Group 1", description="This is the first group.")
    group1.add_argument("-g1A", "--group1A", type=int, help="1st argument in group 1")
    group1.add_argument("-g1B", "--group1B", type=int, help="2nd argument in group 1")

    group2 = parser.add_argument_group(title="Group 2", description="This is the second group.")
    group2.add_argument("-g2A", "--group2A", type=int, help="1st argument in group 2")
    group2.add_argument("-g2B", "--group2B", type=int, help="2nd argument in group 2")

    # Mutually exclusive groups
    group3 = parser.add_mutually_exclusive_group() # No title or description
    group3.add_argument("-m1A", "--mutual1A", type=int, help="1st argument in mutual group 1")
    group3.add_argument("-m1B", "--mutual1B", type=int, help="2nd argument in mutual group 1")

    group4 = parser.add_argument_group(title="Mutual Group 2", description="This is the second mutual group.")
    group4Exclusive = group4.add_mutually_exclusive_group(required=True)
    group4Exclusive.add_argument("-m2A", "--mutual2A", type=int, help="1st argument in mutual group 2")
    group4Exclusive.add_argument("-m2B", "--mutual2B", type=int, help="2nd argument in mutual group 2")

    group5 = parser.add_mutually_exclusive_group(required=True) # No title or description
    group5.add_argument("-m3A", "--mutual3A", type=int, help="1st argument in mutual group 3")
    group5.add_argument("-m3B", "--mutual3B", type=int, help="2nd argument in mutual group 3")

    # Subparsers
    subparsers = parser.add_subparsers(dest="command", help="A Subcommand")

    foo_parser = subparsers.add_parser("foo")
    foo_parser.add_argument("-x", type=int, default=1)

    bar_parser = subparsers.add_parser("bar")
    bar_parser.add_argument("y", type=float)
    bar_parser.add_argument("-s2", "--string2", type=str, help="A string argument")

    third_parser = subparsers.add_parser("third")
    third_parser.add_argument("-b", action="store_true", help="A boolean argument")

    # TODO: Add a subparser within a subparser

    return parser

def runDemo():
    """
    Runs a demonstration of the `argparse` interface with the Argparse Interface attached.

    For CLI: `python .\demo.py -bf -m2A 1 -m3A 2 3 foo`

    For GUI: `python .\demo.py --gui`
    """
    # Get the parser
    parser = getDemoArgParser()

    # Prepare the interface
    interface = Wrapper(
        parser,
        logLevel=logging.DEBUG
    )
    args = interface.parseArgs()

    # Make it pretty
    print("\n")
    if args is not None:
        print("Parsed arguments:\n")
        pprint({k: f"{v} ({type(v).__name__})" for k, v in vars(args).items()})
    else:
        print(f"No arguments parsed:\n{args}")
