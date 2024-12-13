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
        # TODO: More dynamic?
        yield from self.buildParserInputs()

        # TODO: Make tabs for subparsers
        # with TabbedContent():
        #     with TabPane("Foo"):
        #         yield Label("Foo content")
        #     with TabPane("Bar"):
        #         yield Label("Bar content")

        # Add footer
        yield Footer()

    def on_mount(self) -> None:
        self.title = self.mainTitle
        self.sub_title = self.mainSubtitle

    # MARK: UI Builders
    def buildParserInputs(self):
        """
        Yields the UI elements for the parser inputs.
        """
        # Loop through the parser actions
        for action in (a for a in self._parser._actions if not ((self.guiFlag in a.option_strings) or isinstance(a, argparse._HelpAction))):
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
                # TODO: Add this
                self._uiLogger.warning("Subparsers are not yet supported.")
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
        # TODO: Populate with defaults from action

        # Prepare the id for this list
        # listId = f"{action.dest}_list"
        listId = action.dest

        # Create record of the list items
        self._listsData[listId] = (action, items)

        # Add a list input
        yield Vertical(
            Label(action.dest),
            Vertical(
                *items,
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

    def _buildListInputItem(self, id: str, action: argparse.Action):
        """
        Yields a list input item for the given `action`.

        id: The identifier for this list item.
        action: The `argparse` action to build from.
        """
        # Prepare the id for this list item
        itemId = f"{action.dest}_{id}"

        # Get initial value if present
        if isinstance(self._commands[action.dest], dict):
            value = self._commands[action.dest].get(id, None)
        else:
            value = None

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

    # MARK: Functions
    def getArgs(self) -> Optional[dict[str, Optional[Any]]]:
        """
        Returns the parsed arguments from the interface.
        """
        # TODO: CRITICAL: Flatten the list item id: value dict into a list of values for it's dest
        # Also need to handle the intended order...
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

    def bindingSubmit(self) -> None:
        """
        Triggered whe nthe submit binding is activated.
        """
        self.exit()
