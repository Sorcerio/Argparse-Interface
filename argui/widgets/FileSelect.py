# Argparse Interface: File Select Widget
# A widget for selecting a file or directory from the file system.

# MARK: Imports
import uuid
import argparse
from pathlib import Path
from typing import Optional, Union, Callable

from textual import on
from textual.app import App
from textual.dom import DOMNode
from textual.widget import Widget
from textual.widgets import Label, Button, Input, Link
from textual.containers import Vertical, Horizontal
from textual.message import Message

from .. import Utils
from ..modals.FileSelectModal import FileSelectModal

# MARK: Classes
class FileSelect(Widget):
    """
    A widget for selecting a file or directory from the file system.
    """
    # MARK: Constants
    CLASS_FILESELECT_ROOT = "fileSelect"
    CLASS_FILESELECT_BOX = "fileSelectBox"
    CLASS_FILESELECT_LINK_LABEL = "fileSelectLabel"
    CLASS_FILESELECT_OPEN_BTN = "fileSelectButton"

    DEFAULT_CSS = """
    FileSelect {
        height: auto;
        width: 100%;
    }
    """

    # MARK: Lifecycle
    def __init__(self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        disabled: bool = False
    ) -> None:
        """
        name: The name of the input list.
        id: The id of the input list.
        classes: The classes to apply to the input list.
        disabled: If `True`, the input list will be disabled.
        """
        super().__init__(
            name=name,
            id=id,
            classes=((classes or "") + f" {self.CLASS_FILESELECT_ROOT}").strip(),
            disabled=disabled
        )

    def compose(self):
        yield Horizontal(
            Link(
                "No file selected.",
                url="",
                classes=self.CLASS_FILESELECT_LINK_LABEL
            ),
            Button(
                "Select",
                variant="primary",
                classes=self.CLASS_FILESELECT_OPEN_BTN,
                tooltip="Select a file from your system.", # TODO: Change text based on type
            ),
            classes=self.CLASS_FILESELECT_BOX
        )

    # MARK: Events
    class ModalRequested(Message):
        """
        Sent when the File Select modal should be opened.
        """
        def __init__(self, sender: 'FileSelect', showModal: Callable[[App, Optional[Union[str, Path]]], None]) -> None:
            super().__init__()
            self.sender = sender
            self.showModal = showModal

        @property
        def control(self) -> DOMNode | None:
            """
            The `InputList` associated with this message.
            """
            return self.sender

    # MARK: Functions
    def presentFileSelectModal(self,
        app: App,
        startPath: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Presents the file select modal.

        app: The `App` object to present the modal onto.
        """
        # Create the file select return handler
        def fileSelectDone(path: Optional[Path]):
            """
            path: A `Path` object or `None` if the user cancelled.
            """
            # TODO: Replace with an event call!

            # # Check if a path was selected
            # if isinstance(path, Path):
            #     # Update the command
            #     self._commands[dest] = path

            #     # Update the label
            #     linkLabel: Link = self.query_one(f"#{dest}_fileSelectLabel") # TODO: Constants for all ids and classes!
            #     if linkLabel:
            #         linkLabel.update(Utils.limitString(str(path), 42, trimRight=False))
            #         linkLabel.tooltip = str(path)
            #         linkLabel.url = path

        # Push the modal
        app.push_screen(
            FileSelectModal(
                app,
                startPath
            ),
            callback=fileSelectDone
        )

    # MARK: Handlers
    @on(Button.Pressed, f".{CLASS_FILESELECT_OPEN_BTN}")
    def fileSelectOpenButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when a file select's "open" button is pressed to open.
        """
        # Resolve it here
        event.stop()

        # Send the modal message
        self.post_message(self.ModalRequested(
            sender=self,
            showModal=self.presentFileSelectModal
        ))
