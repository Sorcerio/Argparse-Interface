# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
import os
import argparse
import logging
from typing import Optional, Any

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Switch

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
        yield Label("Foo content") # TODO: Remove

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
                # Should it be this? Or should it stay `None` if there's no default?
                self._commands[action.dest] = isinstance(action, argparse._StoreTrueAction)

                # Create the switch
                yield from self._buildSwitchInput(action)
            elif isinstance(action, argparse._SubParsersAction):
                # Add a subparser group
                self._uiLogger.warning("Subparsers are not yet supported.")
            elif isinstance(action, argparse._StoreAction):
                # Decide based on expected type and properties
                if (action.choices is not None):
                    # Add a combo box input
                    self._uiLogger.warning("Dropdown inputs are not yet supported.")
                elif (action.nargs == "+"):
                    # Add a list input
                    self._uiLogger.warning("List inputs are not yet supported.")
                elif action.type == int:
                    # Add an int input
                    self._uiLogger.warning("Int inputs are not yet supported.")
                elif action.type == float:
                    # Add a float input
                    self._uiLogger.warning("qwerty inputs are not yet supported.")
                else:
                    # Add a string input
                    self._uiLogger.warning("String inputs are not yet supported.")
            else:
                # Report
                self._uiLogger.warning(f"Unknown action type: {action}")

        # TODO: Remove
        print(self.getArgs())

    def _buildSwitchInput(self, action: argparse.Action):
        """
        Yields a switch input for the given `action`.

        action: The `argparse` action to build the checkbox for.
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

    # Functions
    def getArgs(self) -> Optional[dict[str, Optional[Any]]]:
        """
        Returns the parsed arguments from the interface.
        """
        return self._commands

    # Handlers
    @on(Switch.Changed, f".{CLASS_SWITCH}")
    def inputSwitchChanged(self, event: Switch.Changed) -> None:
        self._commands[event.switch.id] = event.value
        self._uiLogger.debug(f"Switch changed: {event.switch.id} -> {event.value}")

    def on_button_pressed(self) -> None:
        self.exit()
