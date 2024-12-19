# Argparse Interface: Quit Modal
# An `AlertModal` for confirming the user's intent to quit the application.

# MARK: Imports
from textual.app import App
from textual.widgets import Button

from .AlertModal import AlertModal
from .ReturnCodes import ReturnCodes

# MARK: Classes
class QuitModal(AlertModal):
    """
    A `ModalScreen` object for providing a basic prompt to the user.
    """
    # Constants
    ID_QUIT_BTN = "quitButton"
    ID_CANCEL_BTN = "cancelButton"

    # Lifecycle
    def __init__(self):
        super().__init__(
            "Are you sure you want to quit?",
            [
                Button("Quit", variant="error", id=self.ID_QUIT_BTN),
                Button("Cancel", variant="primary", id=self.ID_CANCEL_BTN)
            ]
        )

    @staticmethod
    def pushScreen(app: App):
        """
        Presents the quit modal as a screen.

        app: The `App` object to present the modal on.
        """
        # Prepare callback
        def quitCallback(event: Button.Pressed):
            if event.button.id == QuitModal.ID_QUIT_BTN:
                app.exit(ReturnCodes.QUIT)

        # Present the modal
        app.push_screen(QuitModal(), callback=quitCallback)
