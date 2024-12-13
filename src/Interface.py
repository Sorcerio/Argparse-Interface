# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
import logging

from textual.app import App, ComposeResult
from textual.widgets import Welcome

from .Logging import getLogger

# MARK: Classes
class Interface(App):
    """
    Automatic interface for the `argparse` module.

    This class is the interface runner for the module.
    Use `Wrapper` to automatically handle the interface.
    """
    # Constructor
    def __init__(self, logLevel: int = logging.WARN) -> None:
        """
        logLevel: The logging level to use.
        """
        super().__init__()

        # Setup
        self._uiLogger = getLogger(logLevel)

    # Functions
    def compose(self) -> ComposeResult:
        yield Welcome()

    def on_button_pressed(self) -> None:
        self.exit()
