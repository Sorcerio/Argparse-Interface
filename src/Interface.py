# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
import os
import argparse
import logging
import uuid
from typing import Union, Optional, Any

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.validation import Number
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Switch, Select, Input, ListView, ListItem, Button

from .Logging import getLogger

# TODO: Add `tooltip` to all inputs with their `help` text!

# MARK: Classes
class Interface(App):
    """
    Automatic interface for the `argparse` module.

    This class is the interface runner for the module.
    Use `Wrapper` to automatically handle the interface.
    """
    # MARK: Constants
    CSS_PATH = os.path.join(os.path.dirname(__file__), "style", "Interface.tcss")
    CLASS_SWITCH = "switchInput"
    CLASS_DROPDOWN = "dropdownInput"
    CLASS_TYPED_TEXT = "textInput"
    CLASS_LIST_RM_BTN = "listRemoveButton"
    CLASS_LIST_ADD_BTN = "listAddButton"
    CLASS_LIST_TEXT = "listInput"
    CLASS_TABS_CONTAINER = "tabsContainer"

    BINDINGS = {
        Binding(
            "ctrl+c", # TODO: Change this back to "ctrl+q"
            "quit",
            "Quit",
            tooltip="Quit without submitting.",
            show=True,
            priority=True
        ),
        Binding(
            "ctrl+s",
            "bindingSubmit",
            "Submit",
            tooltip="Submit.",
            show=True,
            priority=True
        )
    }

    # MARK: Constructor
    def __init__(self,
        parser: argparse.ArgumentParser,
        guiFlag: str, # TODO: General blacklist of args
        title: str = "Argparse Interface",
        subTitle: str = "",
        logLevel: int = logging.WARN
    ) -> None:
        """
        parser: The top-level `ArgumentParser` object to use in the interface.
        guiFlag: The flag to use to indicate that the gui should be shown.
        title: The title of the interface.
        subTitle: The subtitle of the interface.
        logLevel: The logging level to use.
        """
        # Super
        super().__init__()

        # Record data
        self.mainTitle = title
        self.mainSubtitle = subTitle
        self.guiFlag = guiFlag

        self._parser = parser
        self._commands: dict[str, Optional[Any]] = {}
        self._listsData: dict[str, tuple[argparse.Action, dict[str, Any]]] = {} # { list id : (action, {list item id : list item}) }
        self._uiLogger = getLogger(logLevel)

        # Check for the css
        if not os.path.exists(self.CSS_PATH):
            self._uiLogger.error(f"Could not find the css file at: {self.CSS_PATH}")

    # MARK: Lifecycle
    def compose(self) -> ComposeResult:
        # Add header
        yield Header(icon="⛽") # TODO: User supplied text icon

        # Add content
        yield from self._buildParserInputs(self._parser)

        # Add footer
        yield Footer()

    def on_mount(self) -> None:
        self.title = self.mainTitle
        self.sub_title = self.mainSubtitle

    # MARK: UI Builders
    def _buildParserInputs(self, parser: argparse.ArgumentParser):
        """
        Yields the UI elements for the parser inputs.
        """
        # Loop through the parser actions
        for action in (a for a in parser._actions if not ((self.guiFlag in a.option_strings) or isinstance(a, argparse._HelpAction))):
            # Record the parser key
            if action.dest in self._commands:
                self._uiLogger.warning(f"Duplicate command found: {action.dest}")

            self._commands[action.dest] = (action.default or None)

            # Decide what UI to show
            # TODO: Check argparse docs to find any missing deliniations
            if isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
                # Add a switch
                # Set the inferred value
                # self._commands[action.dest] = isinstance(action, argparse._StoreTrueAction)

                # Create the switch
                yield from self._buildSwitchInput(action)
            elif isinstance(action, argparse._SubParsersAction):
                # Add a subparser group
                yield from self._buildSubparserGroup(action)
            elif isinstance(action, argparse._StoreAction):
                # TODO: Add advanced "typed" input types like file select, etc
                # Decide based on expected type and properties
                if (action.choices is not None):
                    # Add a combo box input
                    yield from self._buildDropdownInput(action)
                elif (action.nargs == "+"):
                    # Add a list input
                    yield from self._buildListInput(action)
                elif action.type == int:
                    # Add an int input
                    yield from self._buildTypedInput(action, inputType="integer")
                elif action.type == float:
                    # Add a float input
                    yield from self._buildTypedInput(action, inputType="number")
                else:
                    # Add a string input
                    yield from self._buildTypedInput(action)
            else:
                # Report
                self._uiLogger.warning(f"Unknown action type: {action}")

    def _buildSwitchInput(self, action: argparse.Action):
        """
        Yields a switch input for the given `action`.

        action: The `argparse` action to build from.
        """
        # Add a switch
        yield Horizontal(
            Label(action.dest),
            Switch(
                value=isinstance(action, argparse._StoreTrueAction),
                tooltip=action.help,
                id=action.dest,
                classes=f"{self.CLASS_SWITCH}"
            ),
            classes="hcontainer"
        )

    def _buildDropdownInput(self, action: argparse.Action):
        """
        Yields a dropdown (select) input for the given `action`.

        action: The `argparse` action to build from.
        """
        # Add select dropdown
        yield Horizontal(
            Label(action.dest),
            Select(
                options=[(str(c), c) for c in action.choices],
                value=(action.default if (action.default is not None) else action.choices[0]),
                tooltip=action.help,
                id=action.dest,
                classes=f"{self.CLASS_DROPDOWN}"
            ),
            classes="hcontainer"
        )

    def _createInput(self,
        action: argparse.Action,
        inputType: str = "text",
        name: Optional[str] = None,
        classes: Optional[str] = CLASS_TYPED_TEXT,
        value: Optional[Union[str, int, float]] = None
    ) -> Input:
        """
        Creates a setup `Input` object for the given `action`.
        For the full input group, use `_buildTypedInput(...)`.

        action: The `argparse` action to build from.
        inputType: The type of input to use for the Textual `Input(type=...)` value.
        classes: The classes to add to the input.
        value: The value to set the input to initially.
        """
        # Decide validators
        validators = None
        if action.type == int:
            validators = [Number()]
        elif action.type == float:
            validators = [Number()]

        return Input(
            value=(str(value) if (value is not None) else None),
            placeholder=str(action.metavar or action.dest),
            type=inputType,
            name=name,
            id=action.dest,
            classes=classes,
            validators=validators
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
        yield Horizontal(
            Label(action.dest),
            self._createInput(action, inputType=inputType),
            classes="hcontainer"
        )

    def _buildListInput(self, action: argparse.Action):
        """
        Yields a list input for the given `action`.

        action: The `argparse` action to build from.
        """
        # Prepare item list
        items: dict[str, Any] = {}

        # Add initial values if present
        if isinstance(self._commands[action.dest], list):
            # Process the initial values
            cmdUpdate = {}
            for v in self._commands[action.dest]:
                # Get item id
                itemId = str(uuid.uuid4())

                # Add the UI item to items
                items[itemId] = self._buildListInputItem(
                    itemId,
                    action,
                    value=v
                )

                # Add to command update
                cmdUpdate[itemId] = v

            # Update the command
            self._commands[action.dest] = cmdUpdate

        # Prepare the id for this list
        listId = action.dest

        # Create record of the list items
        self._listsData[listId] = (action, items)

        # Add a list input
        yield Vertical(
            Label(action.dest),
            Vertical(
                *items.values(),
                id=listId,
                classes="vcontainer"
            ),
            Button(
                "Add +",
                name=listId,
                classes=f"{self.CLASS_LIST_ADD_BTN}"
            ),
            classes="itemlist"
        )

    def _buildListInputItem(self, id: str, action: argparse.Action, value: Optional[str] = None):
        """
        Yields a list input item for the given `action`.

        id: The identifier for this list item.
        action: The `argparse` action to build from.
        value: The initial value for this list item.
        """
        # Prepare the id for this list item
        itemId = f"{action.dest}_{id}"

        # Update the command data
        if isinstance(self._commands[action.dest], dict):
            self._commands[action.dest][id] = value
        else:
            self._commands[action.dest] = {id: value}

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

        # Create input
        inputField = self._createInput(
            action,
            inputType=inputType,
            name=itemId,
            classes=self.CLASS_LIST_TEXT,
            value=value
        )

        # Add a list input item
        return Horizontal(
            inputField,
            Button(
                "X",
                name=itemId,
                classes=f"{self.CLASS_LIST_RM_BTN}",
                variant="error"
            ),
            id=itemId,
            classes="item"
        )

    def _buildSubparserGroup(self, action: argparse.Action):
        """
        Yields a subparser group for the given `action`.

        action: The `argparse` action to build from.
        """
        # TODO: Remove subparser's children from command data when switching to a different subparser
        # Add tabs for subparsers
        with TabbedContent(id=action.dest, classes=self.CLASS_TABS_CONTAINER):
            # Loop through subparsers
            parserKey: str
            parser: argparse.ArgumentParser
            for parserKey, parser in action.choices.items():
                # Create the tab
                with TabPane(parserKey, id=f"{action.dest}_{parserKey}"):
                    # Add description
                    if parser.description:
                        yield Label(parser.description)

                    yield from self._buildParserInputs(parser)

    # MARK: Functions
    def getArgs(self) -> Optional[dict[str, Optional[Any]]]:
        """
        Returns the parsed arguments from the interface.
        """
        # TODO: Add UUID order tracking to preserve list element order
        for id in self._listsData.keys():
            # Check if a dict that needs to be flattened
            if (id in self._commands) and isinstance(self._commands[id], dict):
                # Build the update
                cmdUpdate = [v for v in self._commands[id].values()]

                # Apply the update
                self._commands[id] = cmdUpdate

        return self._commands

    # MARK: Private Functions
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

    # MARK: Handlers
    @on(Switch.Changed, f".{CLASS_SWITCH}")
    def inputSwitchChanged(self, event: Switch.Changed) -> None:
        """
        Triggered when an input switch is changed.
        """
        self._commands[event.switch.id] = event.value
        self._uiLogger.debug(f"Switch changed: {event.switch.id} -> {event.value}")

    @on(Select.Changed, f".{CLASS_DROPDOWN}")
    def inputDropdownChanged(self, event: Select.Changed) -> None:
        """
        Triggered when an input dropdown is changed.
        """
        self._commands[event.select.id] = event.value
        self._uiLogger.debug(f"Dropdown changed: {event.select.id} -> {event.value}")

    @on(Input.Changed, f".{CLASS_TYPED_TEXT}")
    def inputTypedChanged(self, event: Input.Changed) -> None:
        """
        Triggered when a typed text input is changed.
        """
        # Get appropriate value type
        val = self._typedStringToValue(event.value, event.input.type)

        # Update
        self._commands[event.input.id] = val
        self._uiLogger.debug(f"Text changed: {event.input.id} -> {val} ({type(val)})")

    @on(Input.Changed, f".{CLASS_LIST_TEXT}")
    def inputTypedChanged(self, event: Input.Changed) -> None:
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
        self._uiLogger.debug(f"List based text changed: {event.input.id} -> {val} ({type(val)})")

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

    @on(Button.Pressed, f".{CLASS_LIST_RM_BTN}")
    def listRemoveButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when a list remove button is pressed.
        """
        # Get the target
        dest, id = event.button.name.split("_")

        # Remove from the command
        _ = self._commands[dest].pop(id)

        # Remove from the list data
        _ = self._listsData[dest][1].pop(id)

        # Remove from the UI
        self.get_widget_by_id(event.button.name).remove()

    @on(TabbedContent.TabActivated, f".{CLASS_TABS_CONTAINER}")
    def tabActivated(self, event: TabbedContent.TabActivated) -> None:
        """
        Triggered when a tab is activated.
        """
        # Get the target
        dest, tabId = event.tab.id.rsplit("-", 1)[-1].split("_")

        # Update the command
        self._commands[dest] = tabId

    def bindingSubmit(self) -> None:
        """
        Triggered whe nthe submit binding is activated.
        """
        self.exit()
