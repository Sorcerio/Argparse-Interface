# Argparse Interface: Alert Modal
# A `ModalScreen` object for providing a basic prompt to the user.

# MARK: Imports
import os
from typing import Optional, Callable, Iterable

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Grid
from textual.screen import ModalScreen
from textual.widgets import Label, Button

# MARK: Classes
class AlertModal(ModalScreen[Button.Pressed]):
    """
    A `ModalScreen` object for providing a basic prompt to the user.
    """
    # Constants
    CSS_PATH = os.path.join(os.path.dirname(__file__), "style", "AlertModal.tcss")
    ID_ALERT_ROOT = "alertModal"
    CLASS_ALERT_BTN = "alertButton"

    # Lifecycle
    def __init__(self,
        message: str,
        buttons: Iterable[Button],
        onButtonPressed: Optional[Callable[[Button.Pressed], None]] = None
    ):
        """
        message: The message to display in the alert.
        buttons: The buttons to display in the alert.
        onButtonPressed: The callback to call when a button is pressed.
        """
        super().__init__()

        # Record data
        self._message = message
        self._buttons = buttons
        self._onButtonPressed = onButtonPressed

        # Add button class
        for btn in self._buttons:
            btn.add_class(self.CLASS_ALERT_BTN)

        # Update button grid
        CSS = f".{self.ID_ALERT_ROOT} > Grid " + "{" + f"grid-size: {len(buttons)} 1;" + "}"

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(self._message),
            # Horizontal(*self._buttons),
            Grid(*self._buttons),
            id=self.ID_ALERT_ROOT
        )

    # Handlers
    @on(Button.Pressed, f".{CLASS_ALERT_BTN}")
    def alertButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when an alert button is pressed.
        """
        # Dismiss the modal
        self.dismiss(event)
