# Argparse Interface: Submit Error Modal
# A modal informing the user of any errors that occurred during submission.

# MARK: Imports
import os
from typing import Iterable

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Button

# MARK: Class
class SubmitErrorModal(ModalScreen):
    """
    A modal informing the user of any errors that occurred during submission.
    """
    # Constants
    CSS_PATH = os.path.join(os.path.dirname(__file__), "..", "style", "SubmitErrorModal.tcss")
    ERROR_INSTRUCTIONS = "Could not submit because of the following issues:"
    ID_CONTAINER = "submitErrorModal"
    ID_BTN_DISMISS = "dismissButton"
    ID_LABEL_INSTR = "instrLabel"
    CLASS_LABEL_ISSUE = "issueLabel"

    # Lifecycle
    def __init__(self, problems: Iterable[str], instr: str = ERROR_INSTRUCTIONS):
        """
        problems: The problems that occurred during submission.
        instr: The instructions to display to the user.
        """
        super().__init__()

        # Record data
        self._problems = problems
        self._instr = instr

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(self._instr, id=self.ID_LABEL_INSTR),
            Vertical(*[Label(f"• {problem}", classes=self.CLASS_LABEL_ISSUE) for problem in self._problems]),
            Button("Dismiss", variant="primary", id=self.ID_BTN_DISMISS),
            id=self.ID_CONTAINER
        )

    # Handlers
    @on(Button.Pressed, f"#{ID_BTN_DISMISS}")
    def dismissButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the dismiss button is pressed.
        """
        # Dismiss the modal
        self.dismiss()
