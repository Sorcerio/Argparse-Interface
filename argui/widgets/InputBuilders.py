# Argparse Interface: Input List Widget
# A widget for rendering and managing a list of input fields for an Action.

# MARK: Imports
import argparse
from typing import Union, Optional

from textual.validation import Number
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Switch, Select, Input, Button, Link

from .FileSelect import FileSelect
from .. import Utils

# MARK: Constants
CLASS_SWITCH = "switchInput"
CLASS_DROPDOWN = "dropdownInput"
CLASS_TYPED_TEXT = "textInput"

# MARK: Functions
def buildSwitchInput(action: argparse.Action):
    """
    Yields a switch input for the given `action`.

    action: The `argparse` action to build from.
    """
    # Add a switch
    yield Vertical(
        Label(Utils.codeStrToTitle(action.dest), classes="inputLabel"),
        Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
        Switch(
            # If by providing the flag the result value is False, then the switch should be the opposite
            value=isinstance(action, argparse._StoreFalseAction),
            tooltip=action.help,
            id=action.dest,
            classes=CLASS_SWITCH
        ),
        classes="inputContainer"
    )

def buildDropdownInput(action: argparse.Action):
    """
    Yields a dropdown (select) input for the given `action`.

    action: The `argparse` action to build from.
    """
    # Add select dropdown
    yield Vertical(
        Label(Utils.codeStrToTitle(action.dest), classes="inputLabel"),
        Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
        Select(
            options=[(str(c), c) for c in action.choices],
            value=(action.default if (action.default is not None) else action.choices[0]),
            tooltip=action.help,
            id=action.dest,
            classes=CLASS_DROPDOWN
        ),
        classes="inputContainer"
    )

def createInput(
    action: argparse.Action,
    inputType: str = "text",
    name: Optional[str] = None,
    classes: Optional[str] = CLASS_TYPED_TEXT,
    value: Optional[Union[str, int, float]] = None,
    metavarIndex: Optional[int] = None
) -> Input:
    """
    Creates a setup `Input` object for the given `action`.
    For the full input group, use `buildTypedInput(...)`.

    action: The `argparse` action to build from.
    inputType: The type of input to use for the Textual `Input(type=...)` value.
    classes: The classes to add to the input.
    value: The value to set the input to initially.
    metavarIndex: The index of the `action.metavar` to use for the placeholder when the `action.metavar` is a tuple.
    """
    # Decide validators
    validators = None
    if action.type == int:
        validators = [Number()]
    elif action.type == float:
        validators = [Number()]

    # Decide placeholder
    if isinstance(action.metavar, tuple):
        placeholder = (str(action.metavar[metavarIndex]) if (isinstance(metavarIndex, int) and (0 <= metavarIndex < len(action.metavar))) else action.dest)
    else:
        placeholder = (str(action.metavar) if action.metavar else action.dest)

    # Send the input
    return Input(
        value=(str(value) if (value is not None) else None),
        placeholder=placeholder.upper(),
        tooltip=action.help,
        type=inputType,
        name=name,
        id=action.dest,
        classes=classes,
        validators=validators
    )

def buildTypedInput(action: argparse.Action, inputType: str = "text"):
    """
    Yields a typed text input group for the given `action`.
    For just the `Input` object, use `createInput(...)`.

    action: The `argparse` action to build from.
    inputType: The type of input to use for the Textual `Input(type=...)` value.
    hideLabel: If `True`, the label will be hidden.
    """
    # Add a typed input
    yield Vertical(
        Label(Utils.codeStrToTitle(action.dest), classes="inputLabel"),
        Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
        createInput(
            action,
            inputType=inputType,
            classes=CLASS_TYPED_TEXT,
            value=(action.default or None)
        ),
        classes="inputContainer"
    )

def buildFileSelectInput(action: argparse.Action):
    """
    Yields an initial interface for a file select input that allows the file select modal to be opened.
    Also tracks the selected file path.

    action: The `argparse` action to build from.
    """
    # Add a file select input
    yield Vertical(
        Label(Utils.codeStrToTitle(action.dest), classes="inputLabel"),
        Label((action.help or f"Supply \"{action.metavar}\"."), classes="inputHelp"),
        FileSelect(
            id=action.dest,
            context=action,
            selectType=action.type
        ),
        classes="inputContainer fileSelectContainer"
    )
