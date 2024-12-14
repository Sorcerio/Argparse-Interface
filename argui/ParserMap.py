# Argparse Interface: Parser Map
# A utility object that maps an `argparse.ArgumentParser` object in a more accessible way.

# MARK: Imports
import uuid
import argparse
from typing import Optional, Iterable

# MARK: Classes
class ParserMap:
    """
    A data object containing the actions for the `argparse` interface sorted by grouping.
    """
    # Constants
    NO_TITLE_GROUP_FLAG = "noTitle"
    REQ_KEY_REQ = "required"
    REQ_KEY_OPT = "optional"

    # Constructor
    def __init__(self, parser: argparse.ArgumentParser):
        """
        Initializes the `ParserMap` object.

        parser: The `argparse.ArgumentParser` object to map.
        """
        self.parser = parser

        # {groupTitle: {"<reqKey>": [action1, action2, ...], "<optKey>": [action1, action2, ...]}}
        self.groupMap = self.deliniateMappedActions(
            self.parser,
            self.mapParserGroups(self.parser)
        )

    # MARK: Static Functions
    @staticmethod
    def mapParserGroups(
        parser: argparse.ArgumentParser,
        groupFlag: str = NO_TITLE_GROUP_FLAG
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

    @staticmethod
    def deliniateMappedActions(
        parser: argparse.ArgumentParser,
        groupMap: dict[str, list[argparse.Action]],
        reqKey: str = REQ_KEY_REQ,
        optKey: str = REQ_KEY_OPT
    ) -> dict[str, dict[str, list[argparse.Action]]]:
        """
        Deliniates the required and optional arguments in the give group mapping.

        parser: The parser that was used to create the `groupMap`.
        groupMap: The group map to deliniate created by `mapParserGroups(...)`.
        reqKey: The key to use for required arguments.
        optKey: The key to use for optional arguments.

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

    @staticmethod
    def parseGroupTitle(t: str) -> Optional[str]:
        """
        Parses the group title from a string.

        t: The string to parse.

        Returns the group title or `None` if the string is not a group title.
        """
        if t.startswith(ParserMap.NO_TITLE_GROUP_FLAG):
            return None

        return t

    @staticmethod
    def excludeActionByDest(
        actions: Iterable[argparse.Action],
        keepHelp: bool = False,
        excludes: Optional[list[str]] = None
    ):
        """
        Generator that excludes actions by their destination.
        """
        return (a for a in actions if not ((a.option_strings in excludes) or (isinstance(a, argparse._HelpAction) and keepHelp)))

    # TODO: Static bool method to ignore help and blacklisted actions

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
        for group, actionSets in self.groupMap.items():
            print(f"Group: {group}")
            for reqOpt, actions in actionSets.items():
                print(f"\t{reqOpt.capitalize()}:")
                for action in actions:
                    print(f"\t\tAction: {action.dest}")
                if len(actions) == 0:
                    print("\t\tno items")
