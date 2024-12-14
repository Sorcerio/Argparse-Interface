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

    # Implicitly required arguments
    parser.add_argument("magicNumber", metavar="NUM", type=int, help="A required int argument")

    # Optional root level arguments
    parser.add_argument("-s", "--string", type=str, help="A string argument")
    parser.add_argument("-i", "--integer", type=int, help="An integer argument", default=32)
    parser.add_argument("-f", "--float", type=float, help="A float argument")
    parser.add_argument("-bt", "--boolTrue", action="store_true", help="A boolean argument")
    parser.add_argument("-bf", "--boolFalse", action="store_false", help="A boolean argument", required=True)
    parser.add_argument("-c", "--choice", type=int, choices=[1, 2, 3], help="A choice argument")
    parser.add_argument("-sz", "--size", help="Specific number of nargs", metavar=("WIDTH", "HEIGHT"), default=None, nargs=2)
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
    bar_parser.add_argument("-s", "--string", type=str, help="A string argument")

    third_parser = subparsers.add_parser("third")
    third_parser.add_argument("-b", action="store_true", help="A boolean argument")

    # TODO: Add a subparser within a subparser

    # MARK: TEST START
    import uuid
    def mapParserGroups(
        parser: argparse.ArgumentParser,
        groupFlag: str = "noTitle"
    ) -> dict[str, list[argparse.Action]]:
        """
        Maps all groups of an `argparse.ArgumentParser` object with their respective actions.

        parser: The `argparse.ArgumentParser` object to map.
        groupFlag: The flag to use for to prefix the UUID of groups without a title.

        Returns a dict of group titles with lists of their respective actions like `{groupTitle: [action1, action2, ...]}`.
        """
        # Get actions of regular groups
        groups = {}
        ownedDests = {}
        for group in parser._action_groups:
            # Create entry
            groups[group.title] = []
            for action in group._group_actions:
                # Add action
                groups[group.title].append(action)

                # Record dest if in general bucket
                ownedDests[action.dest] = group.title

        # Get actions of mutually exclusive groups
        for mutExGroup in parser._mutually_exclusive_groups:
            # Create entry
            groupId = f"{groupFlag}_{uuid.uuid4()}"
            groups[groupId] = []
            for action in mutExGroup._group_actions:
                # Check if action should be recorded
                if action.dest in ownedDests.keys():
                    # Check if in options
                    if (ownedDests[action.dest] == "options"):
                        # Remove from options
                        groups["options"].remove(action)

                        # Add to this group
                        groups[groupId].append(action)

            # Check if empty
            if len(groups[groupId]) == 0:
                # Remove
                del groups[groupId]

        return groups

    def deliniateMappedActions(
        parser: argparse.ArgumentParser,
        groupMap: dict[str, list[argparse.Action]],
        optKey: str = "optional",
        reqKey: str = "required"
    ) -> dict[str, dict[str, list[argparse.Action]]]:
        """
        Deliniates the required and optional arguments in the give group mapping.

        parser: The parser that was used to create the `groupMap`.
        groupMap: The group map to deliniate created by `mapParserGroups(...)`.
        optKey: The key to use for optional arguments.
        reqKey: The key to use for required arguments.

        Returns a dict of group titles with dicts of required and optional actions like `{groupTitle: {"<reqKey>": [action1, action2, ...], "<optKey>": [action1, action2, ...]}}`.
        """
        # Get the mutually exclusive group dest lists
        mutExGroupDests = []
        for group in parser._mutually_exclusive_groups:
            mutExGroupDests.append([action.dest for action in group._group_actions])

        # Loop through the groups
        outGroups = {}
        for groupTitle, groupActions in groupMap.items():
            # Create entry
            outGroups[groupTitle] = {
                reqKey: [],
                optKey: []
            }

            # Check if the whole group is required
            actionDests = [action.dest for action in groupActions]
            if actionDests in mutExGroupDests:
                # Add all to required
                outGroups[groupTitle][reqKey] = groupActions
            else:
                # Add to required and optional
                # Loop through the actions
                for action in groupActions:
                    # Check if required
                    if action.required or (len(action.option_strings) == 0):
                        # Add to required
                        outGroups[groupTitle][reqKey].append(action)
                    else:
                        # Add to optional
                        outGroups[groupTitle][optKey].append(action)

        return outGroups

    groupMap = mapParserGroups(parser)
    for group, actions in groupMap.items():
        print(f"Group: {group}")
        for action in actions:
            print(f"\tAction: {action.dest}")

    print("-----")

    delinGroups = deliniateMappedActions(parser, groupMap)
    for group, actionSets in delinGroups.items():
        print(f"Group: {group}")
        for reqOpt, actions in actionSets.items():
            print(f"\t{reqOpt.capitalize()}:")
            for action in actions:
                print(f"\t\tAction: {action.dest}")
            if len(actions) == 0:
                print("\t\tNone")

    exit()
    # MARK: TEST END

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
        pprint({k: f"{v} ({type(v).__name__})" for k, v in args.items()})
    else:
        print(f"No arguments parsed:\n{args}")
