# Argparse Interface: File Select Directory Type
# A meta type that indicates the interface should only accept directories.

# MARK: Imports
import argparse
from pathlib import Path
from typing import Optional, Iterable

from .MetaType import MetaType

# MARK: Classes
class FileSelectDir(MetaType):
    """
    A meta type that indicates the interface should only accept directories.

    This class should be instantiated when used as in an `argparse.add_argument(...)` call's `type` as such: `argparse.add_argument(type=(...))`.

    No unnamed arguments can be provided to this class.
    Providing any will raise an `argparse.ArgumentTypeError` as this indicates the user is trying to use this class incorrectly.
    """
    # Python Functions
    def __call__(self, value: str) -> Path:
        # Get the path
        try:
            path = Path(value)
        except:
            raise argparse.ArgumentTypeError(f"Value is not a file system path: {value}")

        # Check if the path is a directory
        if not path.is_dir():
            raise argparse.ArgumentTypeError(f"Path does not indicate a directory: {path}")

        return path
