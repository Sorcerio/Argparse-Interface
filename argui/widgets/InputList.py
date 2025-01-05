# Argparse Interface: Input List Widget
# A widget for rendering and managing a list of input fields for an Action.

# MARK: Imports
import uuid
import argparse
from pathlib import Path
from typing import Optional, Any

from textual import on
from textual.dom import DOMNode
from textual.widget import Widget
from textual.widgets import Label, Button, Input
from textual.containers import Vertical, Horizontal
from textual.message import Message

from . import InputBuilders
from .FileSelect import FileSelect
from .. import Utils

# MARK: Classes
class InputList(Widget):
    """
    A widget for rendering and managing a list of input fields for an Action.
    """
    # MARK: Constants
    CLASS_LIST_INPUT_CONTAINER = "listInputContainer"
    CLASS_LIST_INPUT_BOX = "listInputItemBox"
    CLASS_LIST_RM_BTN = "listRemoveButton"
    CLASS_LIST_ADD_BTN = "listAddButton"
    CLASS_LIST_INPUT_TEXT = "listInputText"
    CLASS_LIST_INPUT_PATH = "listInputPath"

    DEFAULT_CSS = """
    InputList {
        height: auto;
        width: 100%;
    }
    """

    # MARK: Lifecycle
    def __init__(self,
        action: argparse.Action,
        showAddRemove: bool,
        defaults: Optional[list[Any]] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        disabled: bool = False
    ) -> None:
        """
        action: The `argparse.Action` to associate with this input list.
        showAddRemove: If `True`, add and remove buttons will be shown.
        defaults: The default values for the input list.
        name: The name of the input list.
        id: The id of the input list.
        classes: The classes to apply to the input list.
        disabled: If `True`, the input list will be disabled.
        """
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled
        )

        self.showAddRemove = showAddRemove
        self._action = action
        self._defaults = defaults
        self._inputs: dict[str, Widget] = {} # { inputId: item }
        self._values: dict[str, Any] = {} # { inputId: value }

        self._prepareInputs()

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

    # MARK: Events
    class InputChanged(Message):
        """
        Sent when any input field value changes.
        """
        def __init__(self, sender: 'InputList', input: Input, value: Any):
            super().__init__()
            self.sender = sender
            self.input = input
            self.value = value

        @property
        def control(self) -> DOMNode | None:
            """
            The `InputList` associated with this message.
            """
            return self.sender

    class InputAdded(Message):
        """
        Sent when a new input field is added.
        """
        def __init__(self, sender: 'InputList', addedWidget: Widget):
            super().__init__()
            self.sender = sender
            self.addedWidget = addedWidget

        @property
        def control(self) -> DOMNode | None:
            """
            The `InputList` associated with this message.
            """
            return self.sender

    class InputRemoved(Message):
        """
        Sent when an input field is removed.
        """
        def __init__(self, sender: 'InputList'):
            super().__init__()
            self.sender = sender

        @property
        def control(self) -> DOMNode | None:
            """
            The `InputList` associated with this message.
            """
            return self.sender

    # MARK: Functions
    def getAction(self) -> argparse.Action:
        """
        Returns the `argparse` action associated with this input list.
        """
        return self._action

    def getValues(self) -> list[Any]:
        """
        Returns the values of the input fields.
        """
        return list(self._values.values())

    # Private Functions
    def _prepareInputs(self):
        """
        Builds the `self._inputs` for the current `self._action`.
        """
        # Add default values if present
        if isinstance(self._defaults, list):
            # Process the default values
            for i, val in enumerate(self._defaults):
                # Get item id
                inputId = str(uuid.uuid4())

                # Add the UI item to items
                self._inputs[inputId] = self._buildListInputItem(
                    inputId,
                    self._action,
                    value=val,
                    showRemove=self.showAddRemove,
                    metavarIndex=i
                )

                # Add to command update
                self._values[inputId] = val

        # Add remaining inputs for nargs
        itemCount = len(self._inputs)
        if isinstance(self._action.nargs, int) and (itemCount < self._action.nargs):
            for i in range(itemCount, (self._action.nargs - itemCount)):
                # Get item id
                inputId = str(uuid.uuid4())

                # Add the UI item to items
                self._inputs[inputId] = self._buildListInputItem(
                    inputId,
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
        inputId = f"{action.dest}_{id}"

        # Update the values
        self._values[id] = value

        # Check if a special type
        if action.type == Path:
            # File Select input
            # Create input and children
            children = [
                FileSelect(
                    classes=self.CLASS_LIST_INPUT_PATH,
                    context=action
                )
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
                    name=inputId,
                    classes=self.CLASS_LIST_INPUT_TEXT,
                    value=value,
                    metavarIndex=metavarIndex
                )
            ]

        # Check if adding the remove button
        if showRemove:
            children.append(Button(
                "X",
                name=inputId,
                classes=f"{self.CLASS_LIST_RM_BTN}",
                variant="error",
                tooltip=f"Remove item"
            ))

        # Add a list input item
        return Horizontal(
            *children,
            id=inputId,
            classes="item"
        )

    # MARK: Handlers
    @on(Input.Changed, f".{CLASS_LIST_INPUT_TEXT}")
    def inputTypedInListChanged(self, event: Input.Changed) -> None:
        """
        Triggered when a typed text input in the list is changed.
        """
        # Resolve it here
        event.stop()

        # Get the target
        dest, id = event.input.name.split("_")

        # Update the value
        value = Utils.typedStringToValue(event.value, event.input.type)
        self._values[id] = Utils.typedStringToValue(event.value, event.input.type)

        # Send the input changed message
        self.post_message(self.InputChanged(
            sender=self,
            input=event.input,
            value=value
        ))

    @on(Button.Pressed, f".{CLASS_LIST_ADD_BTN}")
    def listAddButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when a list add button is pressed.
        """
        # Resolve it here
        event.stop()

        # Create a uuid for the new input
        inputId = str(uuid.uuid4())

        # Create a new input
        newInput = self._buildListInputItem(
            inputId,
            self._action
        )

        # Update the input
        self._inputs[inputId] = newInput

        # Add a new item to the ui
        self.get_widget_by_id(event.button.name).mount(newInput)

        # Check if the list is full
        if isinstance(self._action.nargs, int) and (len(self._inputs) >= self._action.nargs):
            event.button.disabled = True

        # Send the input added message
        self.post_message(self.InputAdded(
            sender=self,
            addedWidget=newInput
        ))

    @on(Button.Pressed, f".{CLASS_LIST_RM_BTN}")
    def listRemoveButtonPressed(self, event: Button.Pressed) -> None:
        """
        Triggered when a list remove button is pressed.
        """
        # Resolve it here
        event.stop()

        # Get the target
        dest, inputId = event.button.name.split("_")

        # Delete the input and value
        del self._inputs[inputId]
        del self._values[inputId]

        # Remove the item from the ui
        self.get_widget_by_id(event.button.name).remove()

        # Check if list is no longer full
        if isinstance(self._action.nargs, int) and (len(self._inputs) < self._action.nargs):
            if addBtn := self.get_widget_by_id(f"{dest}_add"):
                addBtn.disabled = False

        # Send the input removed message
        self.post_message(self.InputRemoved(
            sender=self
        ))
