# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
import os
import argparse
import logging

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label

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
        self._uiLogger = getLogger(logLevel)

        # Check for the css
        if not os.path.exists(self.CSS_PATH):
            self._uiLogger.error(f"Could not find the css file at: {self.CSS_PATH}")

    # Lifecycle
    def compose(self) -> ComposeResult:
        yield Header(icon="⛽") # TODO: User supplied text icon
        yield from self.buildParserInputs()
        # # TODO: Make tabs for subparsers
        # with TabbedContent():
        #     with TabPane("Foo"):
        #         yield Label("Foo content")
        #     with TabPane("Bar"):
        #         yield Label("Bar content")
        yield Footer()

    def on_mount(self) -> None:
        self.title = self.mainTitle
        self.sub_title = self.mainSubtitle

    # UI Builders
    def buildParserInputs(self):
        yield Label("Foo content") # TODO: Remove

        tags = []
        for action in (a for a in self._parser._actions if not ((self.guiFlag in a.option_strings) or isinstance(a, argparse._HelpAction))):
            print(action)

    # Handlers
    def on_button_pressed(self) -> None:
        self.exit()
