# Argparse Interface: Meta Type
# Base class defining meta types that can be used for an `argparse` argument's `type` parameter.

# MARK: Imports
import argparse

# MARK: Classes
class MetaType:
    """
    Base class defining meta types that can be used for an `argparse` argument's `type` parameter.

    This class should be instantiated when used as in an `argparse.add_argument(...)` call's `type` as such: `argparse.add_argument(type=(...))`.

    No unnamed arguments can be provided to this class.
    Providing any will raise an `argparse.ArgumentTypeError` as this indicates the user is trying to use this class incorrectly.
    """
    # Constructor
    def __init__(self, *args):
        # Check if used incorrectly
        if (args is not None) and (len(args) > 0):
            print(args, type(args))
            raise argparse.ArgumentTypeError(f"{self.__class__.__name__} has been implemented incorrectly. Use only keyword arguments and ensure {self.__class__.__name__} is instantiated when used for a `type` like: `argparse.add_argument(type={self.__class__.__name__}(...))`.")
