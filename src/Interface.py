# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
import os
import argparse
import logging
from typing import Optional, Any

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.validation import Number
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Switch, Select, Input, ListView, ListItem, Button

from .Logging import getLogger

# MARK: Classes
class Interface(App):
    """
    Automatic interface for the `argparse` module.

    This class is the interface runner for the module.
    Use `Wrapper` to automatically handle the interface.
    """
    # Constants
    CSS_PATH = os.path.join(os.path.dirname(__file__), "style", "Interface.tcss")
    CLASS_SWITCH = "switchInput"
    CLASS_DROPDOWN = "dropdownInput"
    CLASS_TYPED_TEXT = "textInput"

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

    # Constructor
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
        self._uiLogger = getLogger(logLevel)

        # Check for the css
        if not os.path.exists(self.CSS_PATH):
            self._uiLogger.error(f"Could not find the css file at: {self.CSS_PATH}")

    # Lifecycle
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

    # UI Builders
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

    def _buildTypedInput(self, action: argparse.Action, inputType: str = "text", hideLabel: bool = False):
        """
        Yields a typed text input for the given `action`.

        action: The `argparse` action to build from.
        inputType: The type of input to use for the Textual `Input(type=...)` value.
        hideLabel: If `True`, the label will be hidden.
        """
        # Decide validators
        validators = None
        if action.type == int:
            validators = [Number()]
        elif action.type == float:
            validators = [Number()]

        # Prepare the ui elements
        elements = [
            Input(
                placeholder=str(action.metavar or action.dest),
                type=inputType,
                id=action.dest,
                classes=f"{self.CLASS_TYPED_TEXT}",
                validators=validators
            )
        ]

        # Add label
        if not hideLabel:
            elements.insert(0, Label(action.dest))

        # Add a typed input
        yield Horizontal(
            *elements,
            classes="hcontainer"
        )

    def _buildListInput(self, action: argparse.Action):
        """
        Yields a list input for the given `action`.

        action: The `argparse` action to build from.
        """
        # Prepare the list items
        items = []
        for i in range(5):
            # Add an item
            items.append(self._buildListInputItem(action))

        # Add a list input
        yield Vertical(
            Label(action.dest),
            ListView(
                *items
            ),
            Button("Add +"),
            classes="itemlist"
        )

    def _buildListInputItem(self, action: argparse.Action):
        """
        Yields a list input item for the given `action`.

        action: The `argparse` action to build from.
        """
        # Get proper input
        if action.type == int:
            # Add an int input
            inputField = self._buildTypedInput(action, inputType="integer", hideLabel=True)
        elif action.type == float:
            # Add a float input
            inputField = self._buildTypedInput(action, inputType="number", hideLabel=True)
        else:
            # Add a string input
            inputField = self._buildTypedInput(action, hideLabel=True)

        # Realize the input field
        inputField = list(inputField)[0]
        inputField.classes = "iteminput"

        # Add a list input item
        return ListItem(
            Horizontal(
                inputField,
                Button("X", variant="error")
            ),
            classes="item"
        )

    # Functions
    def getArgs(self) -> Optional[dict[str, Optional[Any]]]:
        """
        Returns the parsed arguments from the interface.
        """
        return self._commands

    # Handlers
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
        try:
            if event.input.type == "integer":
                val = int(event.value)
            elif event.input.type == "number":
                val = float(event.value)
            else:
                val = event.value
        except ValueError:
            val = None

        # Report
        self._commands[event.input.id] = val
        self._uiLogger.debug(f"Text changed: {event.input.id} -> {val} ({type(val)})")

    def bindingSubmit(self) -> None:
        """
        Triggered whe nthe submit binding is activated.
        """
        self.exit()
