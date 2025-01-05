# Argparse Interface: Input List Widget
# A widget for rendering and managing a list of input fields for an Action.

# MARK: Imports
import uuid
import argparse
from pathlib import Path
from typing import Optional, Any

from textual.widget import Widget
from textual.widgets import Label, Button
from textual.containers import Vertical, Horizontal

from . import InputBuilders
from .. import Utils

# MARK: Classes
class InputList(Widget):
    """
    A widget for rendering and managing a list of input fields for an Action.
    """
    # Constants
    CLASS_LIST_INPUT_CONTAINER = "listInputContainer"
    CLASS_LIST_INPUT_BOX = "listInputItemBox"
    CLASS_LIST_RM_BTN = "listRemoveButton"
    CLASS_LIST_ADD_BTN = "listAddButton"
    CLASS_LIST_INPUT_TEXT = "listInputText"

    DEFAULT_CSS = """
    InputList {
        height: auto;
        width: 100%;
    }
    """

    # Lifecycle
    def __init__(self,
        action: argparse.Action,
        showAddRemove: bool,
        defaults: Optional[list[Any]] = None
    ) -> None:
        super().__init__()

        self.showAddRemove = showAddRemove
        self._action = action
        self._defaults = defaults
        self._inputs: dict[str, Widget] = {} # { inputId: item }
        self._values: dict[str, Any] = {} # { inputId: value }

        self._prepareItems()

    def compose(self):
        # Prep the core elements
        uiItems = [
            Label(Utils.codeStrToTitle(self._action.dest), classes="inputLabel"),
            Label((self._action.help or f"Supply \"{self._action.metavar}\"."), classes="inputHelp"),
            Vertical(
                *self._inputs.values(),
                id=self._action.dest,
                classes=self.CLASS_LIST_INPUT_BOX
            )
        ]

        # Yield the add button if enabled
        if self.showAddRemove:
            uiItems.append(Button(
                "Add +",
                id=f"{self._action.dest}_add",
                name=self._action.dest,
                variant="primary",
                classes=f"{self.CLASS_LIST_ADD_BTN}",
                tooltip=f"Add a new item to {Utils.codeStrToTitle(self._action.dest)}",
                disabled=((len(self._inputs) >= self._action.nargs) if isinstance(self._action.nargs, int) else False)
            ))

        # Yield the UI elements
        yield Vertical(
            *uiItems,
            classes=self.CLASS_LIST_INPUT_CONTAINER
        )

        print(self._action.dest, self._inputs)

    # Functions
    def getValues(self) -> list[Any]:
        """
        Returns the values of the input fields.
        """
        return list(self._values.values())

    # Private Functions
    def _prepareItems(self):
        """
        Builds the `self._inputs` for the current `self._action`.
        """
        # Add default values if present
        if isinstance(self._defaults, list):
            # Process the default values
            for i, val in enumerate(self._defaults):
                # Get item id
                itemId = str(uuid.uuid4())

                # Add the UI item to items
                self._inputs[itemId] = self._buildListInputItem(
                    itemId,
                    self._action,
                    value=val,
                    showRemove=self.showAddRemove,
                    metavarIndex=i
                )

                # Add to command update
                self._values[itemId] = val

        # Add remaining inputs for nargs
        itemCount = len(self._inputs)
        if isinstance(self._action.nargs, int) and (itemCount < self._action.nargs):
            for i in range(itemCount, (self._action.nargs - itemCount)):
                # Get item id
                itemId = str(uuid.uuid4())

                # Add the UI item to items
                self._inputs[itemId] = self._buildListInputItem(
                    itemId,
                    self._action,
                    showRemove=self.showAddRemove,
                    metavarIndex=i
                )

    def _buildListInputItem(self,
        id: str,
        action: argparse.Action,
        value: Optional[str] = None,
        showRemove: bool = True,
        metavarIndex: Optional[int] = None
    ):
        """
        Yields a list input item for the given `action`.

        id: The identifier for this list item.
        action: The `argparse` action to build from.
        value: The initial value for this list item.
        showRemove: If `True`, the remove button will be shown for this list item.
        metavarIndex: The index of the `action.metavar` to use for the placeholder when the `action.metavar` is a tuple.
        """
        # Prepare the id for this list item
        itemId = f"{action.dest}_{id}"

        # Update the values
        self._values[id] = value

        # Check if a special type
        if action.type == Path:
            # File Select input
            # Create input and children
            children = [
                InputBuilders.createFileSelectInput(action)
            ]
        else:
            # Standard input
            # Get proper input type
            if action.type == int:
                # An int input
                inputType = "integer"
            elif action.type == float:
                # A float input
                inputType = "number"
            else:
                # A string input
                inputType = "text"

            # Create input and children
            children = [
                InputBuilders.createInput(
                    action,
                    inputType=inputType,
                    name=itemId,
                    classes=self.CLASS_LIST_INPUT_TEXT,
                    value=value,
                    metavarIndex=metavarIndex
                )
            ]

        # Check if adding the remove button
        if showRemove:
            children.append(Button(
                "X",
                name=itemId,
                classes=f"{self.CLASS_LIST_RM_BTN}",
                variant="error",
                tooltip=f"Remove item"
            ))

        # Add a list input item
        return Horizontal(
            *children,
            id=itemId,
            classes="item"
        )
