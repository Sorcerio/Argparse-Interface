# Argparse Interface: File Select Modal
# A modal allowing the user to select a file or directory from the file system.

# MARK: Imports
import os
from pathlib import Path
from typing import Union, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Grid
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input, DirectoryTree

# MARK: Classes
class FileSelectModal(ModalScreen):
    """
    A modal allowing the user to select a file or directory from the file system.
    """
    # Constants
    CSS_PATH = os.path.join(os.path.dirname(__file__), "..", "style", "FileSelectModal.tcss")

    ID_FILE_SELECT_ROOT = "fsModal"
    ID_UP_DIR_BTN = "fsModalUpButton"
    ID_GO_PATH_BTN = "fsModalGoButton"
    ID_PATH_INPUT = "fsModalPathInput"
    ID_CANCEL_BTN = "fsModalCancelButton"
    ID_SELECT_BTN = "fsModalSelectButton"

    # Lifecycle
    def __init__(self, rootPath: Optional[Union[str, Path]]):
        # Super
        super().__init__()

        # Setup root path
        if rootPath is None:
            self._rootPath = os.getcwd()
        else:
            self._rootPath = Path(rootPath)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(
                Button(
                    "^",
                    id=self.ID_UP_DIR_BTN
                ),
                Input( # TODO: Add file path validator?
                    placeholder="~/foo/bar",
                    id=self.ID_PATH_INPUT
                ),
                Button(
                    ">",
                    id=self.ID_GO_PATH_BTN
                )
            ),
            DirectoryTree(self._rootPath),
            Horizontal(
                Button(
                    "Cancel",
                    id=self.ID_CANCEL_BTN
                ),
                Button(
                    "Select",
                    id=self.ID_SELECT_BTN
                )
            ),
            id=self.ID_FILE_SELECT_ROOT
        )

    # Handlers
    @on(Button.Pressed, f"#{ID_UP_DIR_BTN}")
    def dirUpButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        pass # TODO: Implement

    @on(Button.Pressed, f"#{ID_GO_PATH_BTN}")
    def dirUpButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        pass # TODO: Implement

    @on(Button.Pressed, f"#{ID_CANCEL_BTN}")
    def cancelButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        # Dismiss the modal
        self.dismiss(event)

    @on(Button.Pressed, f"#{ID_SELECT_BTN}")
    def pathSelectButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        pass # TODO: Implement
