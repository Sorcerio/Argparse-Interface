# Argparse Interface: Parser Map
# A utility object that maps an `argparse.ArgumentParser` object in a more accessible way.

# MARK: Imports
import uuid
import argparse
from typing import Optional, Iterable

from .ParserGroup import ParserGroup

# MARK: Classes
class ParserMap:
    """
    A utility object that maps an `argparse.ArgumentParser` object in a more accessible way.
    """
    # Constants
    REQ_KEY_REQ = "required"
    REQ_KEY_OPT = "optional"

    # Constructor
    def __init__(self, parser: argparse.ArgumentParser):
        """
        Initializes the `ParserMap` object.

        parser: The `argparse.ArgumentParser` object to map.
        """
        self.parser = parser
        self.groupMap = self.mapParserGroups(parser)

    # MARK: Static Functions
    @staticmethod
    def mapParserGroups(
        parser: argparse.ArgumentParser
    ) -> list[ParserGroup]:
        """
        Maps all groups of an `argparse.ArgumentParser` object with their respective actions.

        parser: The `argparse.ArgumentParser` object to map.

        Returns a list of `ParserGroup` objects.
        """
        # Get actions of regular groups
        groups = []
        ownedDests = {}
        for group in parser._action_groups:
            # Get required and optional actions
            reqActions = []
            optActions = []
            for action in group._group_actions:
                if ParserGroup.isActionRequired(action):
                    reqActions.append(action)
                else:
                    optActions.append(action)

            # Create ParserGroup instance
            parserGroup = ParserGroup(
                isExclusive=False,
                title=group.title,
                reqActions=reqActions,
                optActions=optActions
            )
            groups.append(parserGroup)

            # Record dest if in general bucket
            for action in group._group_actions:
                ownedDests[action.dest] = group.title

        # Get actions of mutually exclusive groups
        for mutExGroup in parser._mutually_exclusive_groups:
            # Create ParserGroup instance
            reqActions = []
            optActions = []
            for action in mutExGroup._group_actions:
                # Check if action should be recorded
                if action.dest in ownedDests.keys():
                    # Check if in options
                    if (ownedDests[action.dest] == "options"):
                        # Remove from options
                        for group in groups:
                            if group.title == "options":
                                group.optActions.remove(action)
                                break

                        # Add to this group
                        if ParserGroup.isActionRequired(action):
                            reqActions.append(action)
                        else:
                            optActions.append(action)

            # Only add the group if it has actions
            if reqActions or optActions:
                parserGroup = ParserGroup(
                    isExclusive=True,
                    reqActions=reqActions,
                    optActions=optActions
                )
                groups.append(parserGroup)

        return groups

    @staticmethod
    def excludeActionByDest(
        actions: Iterable[argparse.Action],
        keepHelp: bool = False,
        excludes: Optional[list[str]] = None
    ):
        """
        Generator that excludes actions by their destination.
        """
        return (a for a in actions if not ((a.option_strings in excludes) or (isinstance(a, argparse._HelpAction) and not keepHelp)))

    # MARK: Functions
    def allActions(self) -> list[argparse.Action]:
        """
        Returns all actions in the parser.
        """
        return self.parser._actions

    def print(self):
        """
        Prints the group map to the console.
        """
        for group in self.groupMap:
            if group.isExclusive:
                infoText = "(exclusive)"
            else:
                infoText = ""
            print(f"Group: {group.title} {infoText}")
            print(f"\tRequired:")
            if group.reqActions:
                for action in group.reqActions:
                    print(f"\t\t{action.dest}")
            else:
                print(f"\t\tno items")
            print(f"\tOptional:")
            if group.optActions:
                for action in group.optActions:
                    print(f"\t\t{action.dest}")
            else:
                print(f"\t\tno items")
