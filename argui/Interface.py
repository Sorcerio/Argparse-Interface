# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
import re
import os
import argparse
import uuid
from pathlib import Path
from typing import Union, Optional, Any, Iterable

from textual import on
from textual.app import App, SystemCommand, ComposeResult
from textual.binding import Binding
from textual.validation import Number
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Switch, Select, Input, Button, Tree

from .Logging import getLogger
from .ParserMap import ParserMap
from .ParserGroup import ParserGroup
from .modals.QuitModal import QuitModal
from .modals.SubmitModal import SubmitModal
from .modals.SubmitErrorModal import SubmitErrorModal
from .debug.ExportDOM import exportDOM

# MARK: Classes
class Interface(App):
    """
    Automatic interface for the `argparse` module.

    This class is the interface runner for the module.
    Use `Wrapper` to automatically handle the interface.
    """
    # MARK: Constants
    CSS_PATH = os.path.join(os.path.dirname(__file__), "style", "Interface.tcss")

    ID_SUBMIT_BTN = "submitButton"
    ID_NAV_AREA = "navArea"
    ID_NAV_TREE = "navTree"
    ID_CONTENT_AREA = "contentArea"

    CLASS_SWITCH = "switchInput"
    CLASS_DROPDOWN = "dropdownInput"
    CLASS_TYPED_TEXT = "textInput"
    CLASS_LIST_RM_BTN = "listRemoveButton"
    CLASS_LIST_ADD_BTN = "listAddButton"
    CLASS_LIST_TEXT = "listInput"
    CLASS_SUBPARSER_TAB_BOX = "subparserContainer"
    CLASS_EXCLUSIVE_TAB_BOX = "exclusiveContainer"
    CLASS_NAV_SECTION = "navSection"
    CLASS_NAV_INPUT = "navInput"

    BINDINGS = {
        Binding(
            "ctrl+q",
            "onQuit",
            "Quit",
            tooltip="Quit without submitting.",
            show=True,
            priority=True,
            system=True
        ),
        Binding(
            "ctrl+s",
            "onSubmit",
            "Submit",
            tooltip="Submit.",
            show=True,
            priority=True,
            system=True
        )
    }

    # MARK: Constructor
    def __init__(self,
        parser: argparse.ArgumentParser,
        guiFlag: str,
        title: str = "Argparse Interface",
        subTitle: Optional[str] = None,
        icon: Optional[str] = "⛽"
    ) -> None:
        """
        parser: The top-level `ArgumentParser` object to use in the interface.
        guiFlag: The flag used to indicate that the gui should be shown. This will be hidden from the interface.
        title: The title of the interface.
        subTitle: The subtitle of the interface.
        icon: A single character icon to display in the header or `None`.
        """
        # Super
        super().__init__()

        # Record data
        self.mainTitle = title
        self.mainSubtitle = subTitle
        self.guiFlag = guiFlag

        self._icon = icon
        self._parserMap = ParserMap(parser)
        self._commands: dict[str, Optional[Any]] = {}
        self._listsData: dict[str, tuple[argparse.Action, dict[str, Any]]] = {} # { list id : (action, { list item id : list item }) }
        self.__initTabsContent: Optional[dict[str, list[argparse.Action]]] = {} # { tab id : [ action, ... ] }; deleted after use

        # Check for the css
        if not os.path.exists(self.CSS_PATH):
            self.log(error=f"Could not find the css file at: {self.CSS_PATH}")

    # MARK: Lifecycle
    def compose(self) -> ComposeResult:
        """
        Defines the interface.
        """
        # Prep the list
        elements = [
            Header(icon=self._icon),
            Horizontal(
                Vertical(
                    self._buildNavigatorArea(),
                    id=self.ID_NAV_AREA
                ),
                Vertical(
                    *self._buildContentArea(),
                    id=self.ID_CONTENT_AREA
                ),
                Footer()
            )
        ]
        return elements

    def on_mount(self) -> None:
        """
        Run after installing the items in `compose()`.
        """
        # Set the theme
        self.theme = "flexoki"

        # Set the title
        self.title = self.mainTitle
        self.sub_title = (self._limitString(self.mainSubtitle, 64) if isinstance(self.mainSubtitle, str) else "")

        # Install any tabs
        for tabsId, actions in self.__initTabsContent.items():
            for action in actions:
                # Check the type of tab being built
                if isinstance(action.choices, dict):
                    # Create a subparser group tab
                    self._installSubparserGroupContent(tabsId, action)
                else:
                    # Create a group content tab
                    self._installTabbedGroupContent(tabsId, action)

        del self.__initTabsContent

        # TODO: Show loading spinner as a screen overlay until this point

    def get_system_commands(self, screen):
        yield from super().get_system_commands(screen)
        yield SystemCommand("Export DOM", "Exports the current DOM to a JSON file.", self._exportDOM)

    # MARK: UI Builders
    def _buildNavigatorArea(self):
        """
        Builds the navigator tree.
        """
        # Build the tree
        tree: Tree[str] = Tree(
            "PROG",
            id=self.ID_NAV_TREE
        )
        tree.root.expand()

        # Populate the tree
        for groupIndex, group in enumerate(self._parserMap.groupMap):
            # Choose a title
            if group.isUuidTitle:
                groupTitle = f"Section {groupIndex + 1}"
            else:
                groupTitle = self._toTitleCase(group.title)

            # Add the group branch
            groupBranch = tree.root.add(
                groupTitle,
                expand=True,
                data=(self.CLASS_NAV_SECTION, group.title)
            )

            # Add the actions
            for action in self._onlyValidActions(group.allActions()):
                # Build the info text
                infoText = ""
                if ParserGroup.isActionRequired(action):
                    infoText += "*"

                # Add the leaf
                groupBranch.add_leaf(
                    f"{self._codeStrToTitle(action.dest)}{infoText}",
                    data=(self.CLASS_NAV_INPUT, action.dest)
                )

        # Add submit leaf
        tree.root.add_leaf(
            "Submit",
            data=(self.CLASS_NAV_INPUT, self.ID_SUBMIT_BTN)
        )

        # Yield the tree
        return tree

    def _buildContentArea(self):
        """
        Builds the input content area.
        """
        # Add content
        if self._parserMap.parser.description:
            yield Label(self._parserMap.parser.description, classes="subtitle")

        yield from self._buildParserInterface()

        if self._parserMap.parser.epilog:
            yield Label(self._parserMap.parser.epilog, classes="epilog")

        # Add submit button
        yield Button(
            "Submit",
            id=self.ID_SUBMIT_BTN,
            variant="success"
        )

    def _buildParserInterface(self):
        """
        Yields all UI elements for the given `argparse.ArgumentParser` object chain.
        UI elements are added to required and optional sections respecting any subparser or group structures.

        parser: The `argparse.ArgumentParser` object to build the UI elements from.
        """
        # Loop through the groups
        for groupIndex, group in enumerate(self._parserMap.groupMap):
            # Check if the group is mutually exclusive
            if group.isExclusive:
                container = Vertical(
                    *self._buildTabbedGroupSections(group),
                    classes="inputGroup exclusive"
                )
            else:
                # Create normal layout
                container = Vertical(
                    *self._buildGroupSections(group),
                    classes="inputGroup normal"
                )

            # Add title
            if group.isUuidTitle:
                container.border_title = f"Section {groupIndex + 1}"
            else:
                container.border_title = self._toTitleCase(group.title)

            # Send it
            yield container

    def _buildGroupSections(self, group: ParserGroup):
        """
        Yields all the UI elements for the actions of any given `ParserGroup`.

        group: The `ParserGroup` to build the UI elements from.
        """
        # Create the required actions as needed
        if group.reqActions:
            yield Label("Required", classes="sectionTitle")
            yield from self._buildActionInputs(
                self._onlyValidActions(group.reqActions)
            )

        # Create the optional actions as needed
        if group.optActions:
            yield Label("Optional", classes="sectionTitle")
            yield from self._buildActionInputs(
                self._onlyValidActions(group.optActions)
            )

    def _buildTabbedGroupSections(self, group: ParserGroup):
        """
        Yields UI elements for actions of any given `ParserGroup` in tabbed sections.
        """
        # Create an id
        tabs = f"group_{group.title}"

        # Store the group actions
        for action in group.allActions():
            # Save for install
            if tabs not in self.__initTabsContent:
                self.__initTabsContent[tabs] = [action]
            else:
                self.__initTabsContent[tabs].append(action)

        # Yield initial content
        yield TabbedContent(id=tabs, classes=self.CLASS_EXCLUSIVE_TAB_BOX)

    def _installTabbedGroupContent(self, tabsId: str, action: argparse.Action):
        """
        Installs a `TabPane` object for given `action` into the `TabbedContent` object with the a matching id.

        tabsId: The id of the `TabbedContent` object to install the `TabPane` objects into.
        action: The `argparse` action to build from.
        """
        # Create the tab
        newTab = TabPane(
            action.dest,
            *self._buildActionInputs([action])
        )

        # Add the tab
        self.get_widget_by_id(tabsId).add_pane(newTab)

    def _buildActionInputs(self, actions: Iterable[argparse.Action]):
        """
        Yields the UI elements for the given `argparse.Action` objects.

        actions: The `argparse.Action` objects to build the UI elements from.
        """
        # Loop through the parser actions
        for action in actions:
            # Record the parser key
            if action.dest in self._commands:
                self.log(warn=f"Duplicate command found: {action.dest}")

            self._commands[action.dest] = (action.default or None) # TODO: Load values from previous run?

            # Decide what UI to show
            # TODO: Check argparse docs to find any missing deliniations
            if isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
                # Add a switch
                yield from self._buildSwitchInput(action)
            elif isinstance(action, argparse._SubParsersAction):
                # Add a subparser group
                yield from self._buildSubparserGroup(action)
            elif isinstance(action, argparse._StoreAction):
                # TODO: Additional advanced "typed" input types
                # Decide based on expected type and properties
                if (action.choices is not None):
                    # Add a combo box input
                    yield from self._buildDropdownInput(action)
                elif ((action.nargs == argparse.ONE_OR_MORE) or
                      (action.nargs == argparse.ZERO_OR_MORE) or
                      (isinstance(action.nargs, int) and (action.nargs > 1))):
                    # Add a list input
                    yield from self._buildListInput(
                        action,
                        showAddRemove=(not (isinstance(action.nargs, int) and (action.nargs > 1)))
                    )
                elif action.type == int:
                    # Add an int input
                    yield from self._buildTypedInput(action, inputType="integer")
                elif action.type == float:
                    # Add a float input
                    yield from self._buildTypedInput(action, inputType="number")
                elif action.type == Path:
                    # Add a file input
                    yield from self._buildFileSelectInput(action)
                else:
                    # Add a string input
                    yield from self._buildTypedInput(action)
            else:
                # Report
                self.log(warn=f"Unknown action type: {action}")

    def _buildSwitchInput(self, action: argparse.Action):
        """
        Yields a switch input for the given `action`.

        action: The `argparse` action to build from.
        """
        # Add a switch
        yield Vertical(
            Label(self._codeStrToTitle(action.dest), classes="inputLabel"),
            Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
            Switch(
                # If by providing the flag the result value is False, then the switch should be the opposite
                value=isinstance(action, argparse._StoreFalseAction),
                tooltip=action.help,
                id=action.dest,
                classes=f"{self.CLASS_SWITCH}"
            ),
            classes="inputContainer"
        )

    def _buildDropdownInput(self, action: argparse.Action):
        """
        Yields a dropdown (select) input for the given `action`.

        action: The `argparse` action to build from.
        """
        # Add select dropdown
        yield Vertical(
            Label(self._codeStrToTitle(action.dest), classes="inputLabel"),
            Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
            Select(
                options=[(str(c), c) for c in action.choices],
                value=(action.default if (action.default is not None) else action.choices[0]),
                tooltip=action.help,
                id=action.dest,
                classes=f"{self.CLASS_DROPDOWN}"
            ),
            classes="inputContainer"
        )

    def _createInput(self,
        action: argparse.Action,
        inputType: str = "text",
        name: Optional[str] = None,
        classes: Optional[str] = CLASS_TYPED_TEXT,
        value: Optional[Union[str, int, float]] = None,
        metavarIndex: Optional[int] = None
    ) -> Input:
        """
        Creates a setup `Input` object for the given `action`.
        For the full input group, use `_buildTypedInput(...)`.

        action: The `argparse` action to build from.
        inputType: The type of input to use for the Textual `Input(type=...)` value.
        classes: The classes to add to the input.
        value: The value to set the input to initially.
        metavarIndex: The index of the `action.metavar` to use for the placeholder when the `action.metavar` is a tuple.
        """
        # Decide validators
        validators = None
        if action.type == int:
            validators = [Number()]
        elif action.type == float:
            validators = [Number()]

        # Decide placeholder
        if isinstance(action.metavar, tuple):
            placeholder = (str(action.metavar[metavarIndex]) if (isinstance(metavarIndex, int) and (0 <= metavarIndex < len(action.metavar))) else action.dest)
        else:
            placeholder = (str(action.metavar) if action.metavar else action.dest)

        # Send the input
        return Input(
            value=(str(value) if (value is not None) else None),
            placeholder=placeholder.upper(),
            tooltip=action.help,
            type=inputType,
            name=name,
            id=action.dest,
            classes=classes,
            validators=validators
        )

    def _createFileSelectInput(self, action: argparse.Action) -> Horizontal:
        """
        Creates a setup `Horizontal` object containing the interface for a file select input for the given `action`.

        action: The `argparse` action to build from.
        """
        return Horizontal(
            Label("No file selected.", id=f"{action.dest}_fileSelectLabel", classes="fileSelectLabel"),
            Button(
                "Select",
                id=action.dest,
                variant="primary",
                classes="fileSelectButton",
                tooltip="Select a file from your system.", # TODO: Change text based on type
            ),
            classes="fileSelectInput"
        )

    def _buildTypedInput(self, action: argparse.Action, inputType: str = "text"):
        """
        Yields a typed text input group for the given `action`.
        For just the `Input` object, use `_createInput(...)`.

        action: The `argparse` action to build from.
        inputType: The type of input to use for the Textual `Input(type=...)` value.
        hideLabel: If `True`, the label will be hidden.
        """
        # Add a typed input
        yield Vertical(
            Label(self._codeStrToTitle(action.dest), classes="inputLabel"),
            Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
            self._createInput(
                action,
                inputType=inputType,
                classes=self.CLASS_TYPED_TEXT,
                value=(action.default or None)
            ),
            classes="inputContainer"
        )

    def _buildFileSelectInput(self, action: argparse.Action):
        """
        Yields an initial interface for a file select input that allows the file select modal to be opened.
        Also tracks the selected file path.

        action: The `argparse` action to build from.
        """
        # Add a file select input
        yield Vertical(
            Label(self._codeStrToTitle(action.dest), classes="inputLabel"),
            Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
            self._createFileSelectInput(action),
            classes="inputContainer fileSelectContainer"
        )

    def _buildListInput(self, action: argparse.Action, showAddRemove: bool = True):
        """
        Yields a list input for the given `action`.

        action: The `argparse` action to build from.
        showAddRemove: If `True`, the add and remove buttons will be shown with a max count defined by `action.nargs`.
        """
        # Prepare item list
        items: dict[str, Any] = {}

        # Add default values if present
        if isinstance(self._commands[action.dest], list):
            # Process the default values
            cmdUpdate = {}
            for i, val in enumerate(self._commands[action.dest]):
                # Get item id
                itemId = str(uuid.uuid4())

                # Add the UI item to items
                items[itemId] = self._buildListInputItem(
                    itemId,
                    action,
                    value=val,
                    showRemove=showAddRemove,
                    metavarIndex=i
                )

                # Add to command update
                cmdUpdate[itemId] = val

            # Update the command
            self._commands[action.dest] = cmdUpdate

        # Add remaining inputs for nargs
        itemCount = len(items)
        if isinstance(action.nargs, int) and (itemCount < action.nargs):
            for i in range(itemCount, (action.nargs - itemCount)):
                # Get item id
                itemId = str(uuid.uuid4())

                # Add the UI item to items
                items[itemId] = self._buildListInputItem(
                    itemId,
                    action,
                    showRemove=showAddRemove,
                    metavarIndex=i
                )

        # Prepare the id for this list
        listId = action.dest

        # Create record of the list items
        self._listsData[listId] = (action, items)

        # Prepare the children
        children = [
            Label(self._codeStrToTitle(action.dest), classes="inputLabel"),
            Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
            Vertical(
                *items.values(),
                id=listId,
                classes="listInputItemBox"
            )
        ]

        if showAddRemove:
            children.append(Button(
                "Add +",
                id=f"{listId}_add",
                name=listId,
                variant="primary",
                classes=f"{self.CLASS_LIST_ADD_BTN}",
                tooltip=f"Add a new item to {self._codeStrToTitle(action.dest)}",
                disabled=((len(items) >= action.nargs) if isinstance(action.nargs, int) else False)
            ))

        # Add a list input
        yield Vertical(
            *children,
            classes="listInputContainer"
        )

    def _buildListInputItem(self,
        id: str,
        action: argparse.Action,
        value: Optional[str] = None,
        showRemove: bool = True,
        metavarIndex: Optional[int] = None
    ):
        """
        Yields a list input item for the given `action`.

        id: The identifier for this list item.
        action: The `argparse` action to build from.
        value: The initial value for this list item.
        showRemove: If `True`, the remove button will be shown for this list item.
        metavarIndex: The index of the `action.metavar` to use for the placeholder when the `action.metavar` is a tuple.
        """
        # Prepare the id for this list item
        itemId = f"{action.dest}_{id}"

        # Update the command data
        if isinstance(self._commands[action.dest], dict):
            self._commands[action.dest][id] = value
        else:
            self._commands[action.dest] = {id: value}

        # Check if a special type
        if action.type == Path:
            # File Select input
            # Create input and children
            children = [
                self._createFileSelectInput(action)
            ]
        else:
            # Standard input
            # Get proper input type
            if action.type == int:
                # An int input
                inputType = "integer"
            elif action.type == float:
                # A float input
                inputType = "number"
            else:
                # A string input
                inputType = "text"

            # Create input and children
            children = [
                self._createInput(
                    action,
                    inputType=inputType,
                    name=itemId,
                    classes=self.CLASS_LIST_TEXT,
                    value=value,
                    metavarIndex=metavarIndex
                )
            ]

        # Check if adding the remove button
        if showRemove:
            children.append(Button(
                "X",
                name=itemId,
                classes=f"{self.CLASS_LIST_RM_BTN}",
                variant="error",
                tooltip=f"Remove item"
            ))

        # Add a list input item
        return Horizontal(
            *children,
            id=itemId,
            classes="item"
        )

    def _buildSubparserGroup(self, action: argparse.Action):
        """
        Yields a subparser group for the given `action`.

        action: The `argparse` action to build from.
        """
        # Guard against bad choices
        if not isinstance(action.choices, dict):
            yield Label("No options provided.")
            return

        # Create an id
        tabs = f"{action.dest}_subparser"

        # Store the action
        if tabs not in self.__initTabsContent:
            self.__initTabsContent[tabs] = [action]
        else:
            self.__initTabsContent[tabs].append(action)

        # Yield the tabbed content
        yield Label(self._codeStrToTitle(action.dest), classes="inputLabel forSubparser")
        yield Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp forSubparser")
        yield TabbedContent(id=tabs, classes=self.CLASS_SUBPARSER_TAB_BOX)

    def _installSubparserGroupContent(self, tabsId: str, action: argparse.Action):
        """
        Installs `TabPane` objects for the given `action` into the `TabbedContent` object with the a matching id.

        tabsId: The id of the `TabbedContent` object to install the `TabPane` objects into.
        action: The `argparse` action to build from.
        """
        # Check the type of tab being built
        if not isinstance(action.choices, dict):
            return

        # Create a subparser group tab
        parserKey: str
        parser: argparse.ArgumentParser
        for parserKey, parser in action.choices.items():
            # Build the tab contents
            children = []

            if parser.description:
                children.append(Label(parser.description))

            children.extend(self._buildActionInputs(self._onlyValidActions(parser._actions)))

            # Create the tab
            newTab = TabPane(
                parserKey,
                *children,
                id=f"{action.dest}_{parserKey}"
            )

            # Add the tab
            self.get_widget_by_id(tabsId).add_pane(newTab)

    # MARK: Functions
    def getArgs(self) -> argparse.Namespace:
        """
        Returns the arguments parsed from the interface.
        """
        # Scope to only active command data
        validDests = self._getValidDests(self._parserMap.parser)

        # Filter out any inactive commands
        filteredCmds = {k: v for k, v in self._commands.items() if k in validDests}

        # Flatten list-based commands
        for id in self._listsData.keys():
            # Check if a dict that needs to be flattened
            if (id in filteredCmds) and isinstance(filteredCmds[id], dict):
                # Build the update
                cmdUpdate = [v for v in filteredCmds[id].values()]

                # Apply the update
                filteredCmds[id] = cmdUpdate

        # return filteredCmds
        return argparse.Namespace(**filteredCmds)

    # MARK: Private Functions
    def _onlyValidActions(self, actions: list[argparse.Action]) -> list[argparse.Action]:
        """
        Gets the valid actions for the given `ArgumentParser` using rules from this Interface.
        """
        return ParserMap.excludeActionByDest(
            actions,
            keepHelp=False,
            excludes=[
                self.guiFlag
            ]
        )

    def _getValidDests(self, parser: argparse.ArgumentParser) -> list[str]:
        """
        Returns a list of valid destinations for the given `ArgumentParser`.

        parser: The parser to get the valid destinations from.
        """
        # Loop through the actions
        validDests = []
        for action in self._onlyValidActions(parser._actions):
            # Check if a subparser
            if isinstance(action, argparse._SubParsersAction):
                # Check if present
                if action.dest in self._commands:
                    # Loop through subparsers
                    for subParserKey, subParser in action.choices.items():
                        # Check if the subparser is active
                        if self._commands[action.dest] == subParserKey:
                            # Record the active subparser's action
                            validDests.append(action.dest)

                            # Check dests in this subparser
                            validDests.extend(self._getValidDests(subParser))
            else:
                # Regular action
                validDests.append(action.dest)

        return validDests

    def _toTitleCase(self, s: str) -> str:
        """
        Converts a string to title case.
        """
        return " ".join([w.capitalize() for w in s.split(" ")])

    def _splitCamelCase(self, s: str) -> str:
        """
        Splits a camel case string into words.
        """
        return " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split())

    def _splitSnakeCase(self, s: str) -> str:
        """
        Splits a snake case string into words.
        """
        return " ".join([w for w in s.split("_")])

    def _codeStrToTitle(self, s: str) -> str:
        """
        Converts a code stlye string (camelCase or snake_case) to a title case string.
        """
        return self._toTitleCase(self._splitCamelCase(self._splitSnakeCase(s)))

    def _typedStringToValue(self, s: str, inputType: str) -> Optional[Union[str, int, float]]:
        """
        Converts a typed input string into an `int`, `float`, the `s` string, or `None`.

        s: The string to convert.
        inputType: The type of input to convert to.

        Returns the converted value.
        """
        try:
            if inputType == "integer":
                return int(s)
            elif inputType == "number":
                return float(s)
            else:
                return s
        except ValueError:
            return None

    def _exportDOM(self) -> None:
        """
        Exports the Textual DOM that is currently displayed.
        """
        exportDOM(self.screen)

    def _limitString(self, s: str, maxChars: int, postfix: str = "...") -> str:
        """
        Limits a string to a certain number of characters, adding a postfix if the string is longer than the limit.
        Takes the length of the postfix into account.

        s: The string to limit.
        maxChars: The maximum number of characters the string should have.
        postfix: The postfix to add to the string if it is longer than the limit.

        Returns a string with a length less than or equal to `maxChars`.
        """
        if not isinstance(s, str):
            raise ValueError("`s` must be a string.")
        if len(s) <= maxChars:
            return s
        return s[:maxChars - len(postfix) + 1] + postfix

    # MARK: Actions
    def action_onQuit(self):
        """
        Triggers when the user cancels submission and execution.
        """
        # Push quit confirmation
        QuitModal.pushScreen(self)

    def action_onSubmit(self):
        """
        Triggers when the user submits the form.
        """
        # Check if all required fields are filled
        # TODO: Add deeper validation checking (piggyback on argparse?)
        reqActions = self._parserMap.allRequiredActions()
        missingRequired = [action.dest for action in reqActions if ((action.dest not in self._commands) or (self._commands[action.dest] is None))]
        if len(missingRequired) > 0:
            # Report
            self.log(warn="Tried to submit without all required inputs.")

            # Push error modal
            self.push_screen(SubmitErrorModal(
                [f"Missing required input: {dest}" for dest in missingRequired]
            ))
        else:
            # Push submit confirmation
            SubmitModal.pushScreen(self)

    # MARK: Handlers
    @on(Switch.Changed, f".{CLASS_SWITCH}")
    def inputSwitchChanged(self, event: Switch.Changed) -> None:
        """
        Triggered when an input switch is changed.
        """
        self._commands[event.switch.id] = event.value
        self.log(debug=f"Switch changed: {event.switch.id} -> {event.value}")

    @on(Select.Changed, f".{CLASS_DROPDOWN}")
    def inputDropdownChanged(self, event: Select.Changed) -> None:
        """
        Triggered when an input dropdown is changed.
        """
        self._commands[event.select.id] = event.value
        self.log(debug=f"Dropdown changed: {event.select.id} -> {event.value}")

    @on(Input.Changed, f".{CLASS_TYPED_TEXT}")
    def inputTypedChanged(self, event: Input.Changed) -> None:
        """
        Triggered when a typed text input is changed.
        """
        # Get appropriate value type
        val = self._typedStringToValue(event.value, event.input.type)

        # Update
        self._commands[event.input.id] = val
        self.log(debug=f"Text changed: {event.input.id} -> {val} ({type(val)})")

    @on(Input.Changed, f".{CLASS_LIST_TEXT}")
    def inputTypedInListChanged(self, event: Input.Changed) -> None:
        """
        Triggered when a typed text input *within a list* is changed.
        """
        # Get the target
        dest, id = event.input.name.split("_")

        # Get appropriate value type
        val = self._typedStringToValue(event.value, event.input.type)

        # Update the command
        self._commands[dest][id] = val

        # Report
        self.log(debug=f"List based text changed: {event.input.id} -> {val} ({type(val)})")

    @on(Button.Pressed, f".{CLASS_LIST_ADD_BTN}")
    def listAddButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when a list add button is pressed.
        """
        # Unpack the data
        action, listItems = self._listsData[event.button.name]

        # Get the uuid for this button
        buttonId = str(uuid.uuid4())

        # Create the list item
        listItem = self._buildListInputItem(
            buttonId,
            action
        )

        # Update the lists data
        listItems[buttonId] = listItem

        # Add a new item to the ui
        self.get_widget_by_id(event.button.name).mount(listItem)

        # Check if the list is full
        if isinstance(action.nargs, int) and (len(listItems) >= action.nargs):
            event.button.disabled = True
            return

    @on(Button.Pressed, f".{CLASS_LIST_RM_BTN}")
    def listRemoveButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when a list remove button is pressed.
        """
        # Get the target
        dest, listId = event.button.name.split("_")
        action, listItems = self._listsData[dest]

        # Remove from the command
        _ = self._commands[dest].pop(listId)

        # Remove from the list data
        del listItems[listId]

        # Remove from the UI
        self.get_widget_by_id(event.button.name).remove()

        # Check if list is no longer full
        if isinstance(action.nargs, int) and (len(listItems) < action.nargs):
            if addBtn := self.get_widget_by_id(f"{dest}_add"):
                addBtn.disabled = False

    @on(TabbedContent.TabActivated, f".{CLASS_SUBPARSER_TAB_BOX}")
    def tabActivated(self, event: TabbedContent.TabActivated) -> None:
        """
        Triggered when a tab is activated.
        """
        # Get the target
        dest, tabId = event.tab.id.rsplit("-", 1)[-1].split("_")

        # Update the command
        self._commands[dest] = tabId

    @on(Button.Pressed, f"#{ID_SUBMIT_BTN}")
    def submitButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when submitting the form.
        """
        self.action_onSubmit()

    @on(Tree.NodeSelected, f"#{ID_NAV_TREE}")
    def navTreeNodeSelected(self, event: Tree.NodeSelected) -> None:
        """
        Triggered when submitting the form.
        """
        # Check for expected data
        if isinstance(event.node.data, tuple):
            # Check for a navigatable node
            nodeType: str
            dest: str
            nodeType, dest = event.node.data
            if nodeType == self.CLASS_NAV_INPUT:
                # Get the target
                target = self.query_one(f"#{dest}")
                scrollArea = self.query_one(f"#{self.ID_CONTENT_AREA}")
                if target and scrollArea:
                    scrollArea.scroll_to_widget(target)
