# Argparse Interface: File Select Widget
# A widget for selecting a file or directory from the file system.

# MARK: Imports
import uuid
import argparse
from pathlib import Path
from typing import Optional, Union, Callable, Any

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
    # TODO: Add file select type (any, any file, file with exts, dir, etc)
    # ^[need to have a way to connect extra data with an argparse argument for this!]
    def __init__(self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        disabled: bool = False,
        context: Optional[Any] = None
    ) -> None:
        """
        name: The name of the file select.
        id: The id of the file select.
        classes: The classes to apply to the file select.
        disabled: If `True`, the file select will be disabled.
        context: Any context to associate with the file select. This will be included in all event messages.
        """
        super().__init__(
            name=name,
            id=id,
            classes=((classes or "") + f" {self.CLASS_FILESELECT_ROOT}").strip(),
            disabled=disabled
        )

        self.context = context
        self.__linkLabel: Optional[Link] = None # Populated in `compose()`

    def compose(self):
        # Record the link element
        self.__linkLabel = Link(
            "No file selected.",
            url="",
            classes=self.CLASS_FILESELECT_LINK_LABEL
        )

        # Yield the interface
        yield Horizontal(
            self.__linkLabel,
            Button(
                "Select",
                variant="primary",
                classes=self.CLASS_FILESELECT_OPEN_BTN,
                tooltip="Select a file from your system.", # TODO: Change text based on select type
            ),
            classes=self.CLASS_FILESELECT_BOX
        )

    # MARK: Events
    class ModalRequested(Message):
        """
        Sent when the File Select modal should be opened.
        """
        def __init__(self,
            sender: 'FileSelect',
            context: Optional[Any],
            showModal: Callable[[App, Optional[Union[str, Path]]], None]
        ) -> None:
            super().__init__()
            self.sender = sender
            self.context = context
            self.showModal = showModal

        @property
        def control(self) -> DOMNode | None:
            """
            The `FileSelect` associated with this message.
            """
            return self.sender

    class FileSelectComplete(Message):
        """
        Sent when a File Select modal has been closed with or without a selection.
        `path` is `None` if the user cancelled or a `Path` object if a file was selected.
        """
        def __init__(self,
            sender: 'FileSelect',
            context: Optional[Any],
            path: Optional[Path]
        ) -> None:
            super().__init__()
            self.sender = sender
            self.context = context
            self.path = path

        @property
        def control(self) -> DOMNode | None:
            """
            The `FileSelect` associated with this message.
            """
            return self.sender

    # MARK: Functions
    def getPath(self) -> Path:
        """
        Returns the current path of the file select.
        """
        return Path(self.__linkLabel.url)

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
            # Send the message
            self.post_message(self.FileSelectComplete(
                sender=self,
                context=self.context,
                path=path
            ))

            # Update the label
            if isinstance(path, Path):
                self.__linkLabel.update(Utils.limitString(str(path), 42, trimRight=False))
                self.__linkLabel.tooltip = str(path)
                self.__linkLabel.url = path

        # Push the modal
        app.push_screen(
            FileSelectModal(startPath),
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
            context=self.context,
            showModal=self.presentFileSelectModal
        ))
