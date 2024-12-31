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
    ID_PATH_BAR = "fsModalPathBar"
    ID_UP_DIR_BTN = "fsModalUpButton"
    ID_PATH_INPUT = "fsModalPathInput"
    ID_GO_PATH_BTN = "fsModalGoButton"
    ID_FILE_TREE = "fsModalFileTree"
    ID_ACTIONS_BAR = "fsModalActionsBar"
    ID_CANCEL_BTN = "fsModalCancelButton"
    ID_SELECT_BTN = "fsModalSelectButton"

    # Lifecycle
    def __init__(self, startPath: Optional[Union[str, Path]]):
        # Super
        super().__init__()

        # Setup paths
        if startPath is None:
            self._startPath = Path.home().resolve()
        else:
            self._startPath = Path(startPath)

        self.__curPath = self._startPath

        # Declare Dir Tree
        self._dirTree: Optional[DirectoryTree] = None # Set in `compose`

    def compose(self) -> ComposeResult:
        # Prepare the dir tree
        self._dirTree = DirectoryTree(
            self._startPath,
            id=self.ID_FILE_TREE
        )

        # Yield it
        yield Vertical(
            Horizontal(
                # Button(
                #     "Up",
                #     id=self.ID_UP_DIR_BTN
                # ),
                Input( # TODO: Add file path validator?
                    value=str(self._startPath.resolve()),
                    placeholder="~/foo/bar",
                    id=self.ID_PATH_INPUT
                ),
                Button(
                    "Go",
                    variant="primary",
                    id=self.ID_GO_PATH_BTN
                ),
                id=self.ID_PATH_BAR
            ),
            self._dirTree,
            Horizontal(
                Button(
                    "Cancel",
                    variant="error",
                    id=self.ID_CANCEL_BTN
                ),
                Button(
                    "Select",
                    variant="success",
                    id=self.ID_SELECT_BTN
                ),
                id=self.ID_ACTIONS_BAR
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

    @on(DirectoryTree.FileSelected, f"#{ID_FILE_TREE}")
    def dirTreeFileSelected(self, event: DirectoryTree.FileSelected) -> None:
        """
        Triggered when a file is selected in the directory tree.
        """
        print(event)
        print("FILE ID", event.node.id)

    @on(DirectoryTree.DirectorySelected, f"#{ID_FILE_TREE}")
    def dirTreeDirSelected(self, event: DirectoryTree.DirectorySelected) -> None:
        """
        Triggered when a directory is selected in the directory tree.
        """
        # Get the new path
        self.__curPath = event.path.resolve()

        # Enter the directory
        self._dirTree.path = str(self.__curPath)
