# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
import logging

from textual.app import App, ComposeResult
from textual.widgets import Welcome, Header

from .Logging import getLogger

# MARK: Classes
class Interface(App):
    """
    Automatic interface for the `argparse` module.

    This class is the interface runner for the module.
    Use `Wrapper` to automatically handle the interface.
    """
    # MARK: Constants
    DEF_TITLE = "Argparse Interface"
    DEF_SUB_TITLE = ""

    # Constructor
    def __init__(self,
        title: str = DEF_TITLE,
        subTitle: str = DEF_SUB_TITLE,
        logLevel: int = logging.WARN
    ) -> None:
        """
        title: The title of the interface.
        subTitle: The subtitle of the interface.
        logLevel: The logging level to use.
        """
        # Super
        super().__init__()

        # Record data
        self.mainTitle = title
        self.mainSubtitle = subTitle
        self._uiLogger = getLogger(logLevel)

    # Functions
    def compose(self) -> ComposeResult:
        yield Header(icon="⛽")
        yield Welcome()

    def on_mount(self) -> None:
        self.title = self.mainTitle
        self.sub_title = self.mainSubtitle

    def on_button_pressed(self) -> None:
        self.exit()
