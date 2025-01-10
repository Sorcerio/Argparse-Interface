# Argparse Interface: File Select File Type
# A stand-in type that indicates the interface should only accept files.

# MARK: Imports
import argparse
from pathlib import Path
from typing import Optional, Iterable

# MARK: Classes
class FileSelectFile:
    """
    A stand-in type that indicates the interface should only accept files.

    This class should be instantiated when used as in an `argparse.add_argument(...)` call's `type` as such: `argparse.add_argument(type=(...))`.

    No unnamed arguments can be provided to this class.
    Providing any will raise an `argparse.ArgumentTypeError` as this indicates the user is trying to use this class incorrectly.
    """
    # Constructor
    def __init__(self, *args, exts: Optional[Iterable[str]] = None):
        """
        exts: The file extensions to accept. Case-insensitive. Provide `None` to accept any file extension.
        """
        # Setup file extensions
        self.validExts = exts

        if self.validExts is not None:
            self.validExts = [ext.lower().lstrip(".") for ext in self.validExts]

        # Check if used incorrectly
        if (args is not None) and (len(args) > 0):
            print(args, type(args))
            raise argparse.ArgumentTypeError(f"{self.__class__.__name__} has been implemented incorrectly. Use only keyword arguments and ensure {self.__class__.__name__} is instantiated when used for a `type` like: `argparse.add_argument(type={self.__class__.__name__}(...))`.")

    # Python Functions
    def __call__(self, value: str) -> Path:
        # Get the path
        try:
            path = Path(value)
        except:
            raise argparse.ArgumentTypeError(f"Value is not a Path: {value}")

        # Check if the path is a file
        if not path.is_file():
            raise argparse.ArgumentTypeError(f"Path does not indicate a file: {path}")

        # Check file extensions
        if self.validExts is not None:
            cleanExt = path.suffix.lower().lstrip(".")
            if cleanExt not in self.validExts:
                validExtsDotted = [f".{ext}" for ext in self.validExts]
                raise argparse.ArgumentTypeError(f"File extension `.{cleanExt}` is not a valid extension for this argument. Valid extensions are: {', '.join(validExtsDotted)}")

        return path
