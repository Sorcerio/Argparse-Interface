# Argparse Interface: File Select Modal
# A modal allowing the user to select a file or directory from the file system.

# MARK: Imports
import os
from pathlib import Path
from typing import Union, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, DirectoryTree

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
    def __init__(self, app: App, startPath: Optional[Union[str, Path]]):
        """
        app: The `App` object that this modal is attached to.
        startPath: The path to start the modal at.
        """
        # Super
        super().__init__()

        # Data
        self._app = app

        # Setup start path
        if startPath is None:
            self._startPath = Path.home().resolve()
        else:
            self._startPath = Path(startPath).resolve()

        # Make sure the start path is a directory
        if not self._startPath.is_dir():
            self._startPath = self._startPath.parent.resolve()

        # Set the current path
        self.__curPath = self._startPath

        # Declare ui elements
        self._dirTree: Optional[DirectoryTree] = None # Set in `compose`
        self._pathInput: Optional[Input] = None # Set in `compose`

    def compose(self) -> ComposeResult:
        # Prepare the dir tree
        self._dirTree = DirectoryTree(
            self._startPath,
            id=self.ID_FILE_TREE
        )

        # Prepare the path input
        self._pathInput = Input( # TODO: Add file path validator?
            value=str(self._startPath.resolve()),
            placeholder="~/foo/bar",
            id=self.ID_PATH_INPUT
        )

        # Yield it
        yield Vertical(
            Horizontal(
                Button(
                    "Back",
                    id=self.ID_UP_DIR_BTN
                ),
                self._pathInput,
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

    # Functions
    def goToPathOrFail(self, path: Union[str, Path]) -> None:
        """
        Navigates to the given `path` or throws a `FileNotFoundError` if the `path` does not exist.
        If the `path` is a directory, it will enter the directory.

        Use `goToPath(...)` to do nothing if the path does not exist.

        path: A path to navigate to. File or directory.
        """
        # Get the proposed path
        path = Path(path).resolve()

        # Check if the path is valid
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        # Update the current path
        self.__curPath = path

        # Check if the path is a directory
        if self.__curPath.is_dir():
            # Enter the directory
            self._dirTree.path = str(self.__curPath)

        # Update the path input
        self._pathInput.value = str(self.__curPath)

    def goToPath(self, path: Union[str, Path]) -> None:
        """
        Navigates to the given `path` if it exists or does nothing.
        If the `path` is a directory, it will enter the directory.

        Use `goToPathOrFail(...)` to throw an error if the path does not exist.

        path: A path to navigate to. File or directory.
        """
        try:
            self.goToPathOrFail(path)
        except FileNotFoundError:
            pass

    # Handlers
    @on(Button.Pressed, f"#{ID_UP_DIR_BTN}")
    def dirUpButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        # Go to it
        self.goToPath(self.__curPath.parent)

    @on(Button.Pressed, f"#{ID_GO_PATH_BTN}")
    def pathGoButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        # Go to it or fail
        try:
            self.goToPathOrFail(self._pathInput.value)
        except FileNotFoundError:
            self.app.notify(
                f"Path does not exist: {self._pathInput.value}",
                severity="warning"
            )

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
        # Go to it
        self.goToPath(event.path)

    @on(DirectoryTree.DirectorySelected, f"#{ID_FILE_TREE}")
    def dirTreeDirSelected(self, event: DirectoryTree.DirectorySelected) -> None:
        """
        Triggered when a directory is selected in the directory tree.
        """
        # Go to it
        self.goToPath(event.path)
