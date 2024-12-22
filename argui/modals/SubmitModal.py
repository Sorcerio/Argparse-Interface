# Argparse Interface: Submit Modal
# An `AlertModal` for confirming the user's intent to submit entered information.

# MARK: Imports
from textual.app import App
from textual.widgets import Button

from .AlertModal import AlertModal
from ..ReturnCodes import ReturnCodes

# MARK: Classes
class SubmitModal(AlertModal):
    """
    An `AlertModal` for confirming the user's intent to submit entered information.
    """
    # Constants
    ID_CONFIRM_BTN = "confirmButton"
    ID_CANCEL_BTN = "cancelButton"

    # Lifecycle
    def __init__(self):
        super().__init__(
            "Are you sure you want to submit?",
            [
                Button("Submit", variant="success", id=self.ID_CONFIRM_BTN),
                Button("Cancel", variant="primary", id=self.ID_CANCEL_BTN)
            ]
        )

    @staticmethod
    def pushScreen(app: App):
        """
        Presents the submit modal as a screen.

        app: The `App` object to present the modal on.
        """
        # Prepare callback
        def submitCallback(event: Button.Pressed):
            if event.button.id == SubmitModal.ID_CONFIRM_BTN:
                app.exit(ReturnCodes.SUBMIT)

        # Present the modal
        app.push_screen(SubmitModal(), callback=submitCallback)
