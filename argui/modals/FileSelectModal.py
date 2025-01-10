# Argparse Interface: File Select Modal
# A modal allowing the user to select a file or directory from the file system.

# MARK: Imports
import os
from pathlib import Path
from typing import Union, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, DirectoryTree

from ..types import FileSelectFile, FileSelectDir

# MARK: Classes
class FileSelectModal(ModalScreen[Optional[Path]]):
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
    def __init__(self,
        startPath: Optional[Union[str, Path]],
        selectType: Optional[Union[FileSelectFile, FileSelectDir]] = None
    ):
        """
        startPath: The path to start the modal at.
        selectType: The type of path to allow as a selection. If `None`, any type of path (file with any extension or directory) is allowed.
        """
        # Super
        super().__init__()

        # Setup start path
        if startPath is None:
            self._startPath = self.fullpath(Path.home())
        else:
            self._startPath = self.fullpath(startPath)

        # Make sure the start path is a directory
        if not self._startPath.is_dir():
            self._startPath = self.fullpath(self._startPath.parent)

        # Set the current path
        self.__curPath = self._startPath

        # Set the select type
        if isinstance(selectType, (FileSelectFile, FileSelectDir)):
            self.selectType = selectType
        else:
            self.selectType = None

        # Declare ui elements
        self._dirTree: Optional[DirectoryTree] = None # Set in `compose`
        self._pathInput: Optional[Input] = None # Set in `compose`

    def compose(self) -> ComposeResult:
        # Decide select button text
        if isinstance(self.selectType, FileSelectFile):
            selectText = "Select File"
        elif isinstance(self.selectType, FileSelectDir):
            selectText = "Select Directory"
        else:
            selectText = "Select"

        # Prepare the dir tree
        self._dirTree = DirectoryTree(
            self._startPath,
            id=self.ID_FILE_TREE
        )

        # Prepare the path input
        self._pathInput = Input( # TODO: Add file path validator?
            value=str(self.fullpath(self._startPath)),
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
                    selectText,
                    variant="success",
                    id=self.ID_SELECT_BTN
                ),
                id=self.ID_ACTIONS_BAR
            ),
            id=self.ID_FILE_SELECT_ROOT
        )

    # Functions
    def fullpath(self, path: Union[str, Path]) -> Path:
        """
        Returns the true full path of the given `path`.
        """
        return Path(path).expanduser().resolve()

    def goToPath(self, path: Union[str, Path], refreshForFile: bool = False) -> None:
        """
        Navigates to the given `path`.
        If the `path` is a directory, it will enter the directory.

        path: A path to navigate to. File or directory.
        refreshForFile: If `True`, the directory tree will refresh it's content based on the directory the file is in. Otherwise, only the directory tree itself won't be changed.
        """
        # Update the current path
        self.__curPath = self.fullpath(path)

        # Check if the path is a directory
        if self.__curPath.is_dir():
            # Enter the directory
            self._dirTree.path = str(self.__curPath)
        elif (refreshForFile and self.__curPath.is_file()):
            # Enter the parent directory
            self._dirTree.path = str(self.fullpath(self.__curPath.parent))

        # Update the path input
        self._pathInput.value = str(self.__curPath)

    # Handlers
    @on(Button.Pressed, f"#{ID_UP_DIR_BTN}")
    def dirUpButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        # Get the previous directory
        if self.__curPath.is_file():
            # Go up to the current dir and up one dir
            upPath = self.__curPath.parent.parent
        else:
            # Go up one directory
            upPath = self.__curPath.parent

        # Go to it
        self.goToPath(upPath)

    @on(Button.Pressed, f"#{ID_GO_PATH_BTN}")
    def pathGoButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        # Go to it
        self.goToPath(self._pathInput.value, refreshForFile=True)

    @on(Button.Pressed, f"#{ID_CANCEL_BTN}")
    def cancelButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        # Dismiss the modal with nothing
        self.dismiss(None)

    @on(Button.Pressed, f"#{ID_SELECT_BTN}")
    def pathSelectButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when the up directory button is pressed.
        """
        # Dismiss the modal with the selected path
        self.dismiss(self.fullpath(self.__curPath))

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
