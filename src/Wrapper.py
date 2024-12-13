# Argparse Interface: Wrapper
# Host wrapper for the Interface.

# MARK: Imports
import argparse
import logging
from typing import Union, Optional, Any

from .Interface import Interface

# MARK: Classes
class Wrapper:
    """
    Automatic interface wrapper for the `argparse` module.

    Use this class to automatically handle the interface.
    """
    # Constants
    LOGGER_NAME = "ArgparseInterface"

    # Constructor
    def __init__(self,
        parser: argparse.ArgumentParser,
        guiFlag: str = "--gui",
        logLevel: int = logging.INFO, # TODO: use WARN
        debugUI: bool = False,
    ):
        """
        parser: The top-level `ArgumentParser` object to use in the interface.
        guiFlag: The flag to use to indicate that the gui should be shown.
        logLevel: The logging level to use.
        debugUI: If `True`, the debug elements will be shown.
        """
        # Record data
        self._parser = parser
        self.guiFlag = guiFlag
        self.showDebugUI = debugUI

        # Logger setup
        self._logger = logging.getLogger(self.LOGGER_NAME)
        self._logger.setLevel(logLevel)

        # Setup log handler
        logHandler = logging.StreamHandler()
        logHandler.setLevel(logLevel)
        formatter = logging.Formatter("[%(levelname)s | %(asctime)s] %(message)s")
        logHandler.setFormatter(formatter)
        self._logger.addHandler(logHandler)

        # Add the gui argument to the parser
        self._addGuiArgument(self._parser)

    # Functions
    def parseArgs(self) -> Optional[argparse.Namespace]:
        """
        Parses the arguments using the method defined by the cli flags.
        Will open the gui if prompted.
        Otherwise, will parse the cli arguments as normal.

        Returns any parsed arguments.
        """
        # Create gui argument parser
        guiArgParser = argparse.ArgumentParser(add_help=False)
        self._addGuiArgument(guiArgParser)

        # Parse the cli args
        args = guiArgParser.parse_known_args()[0]

        # Check if the gui flag is present
        if hasattr(args, self.guiFlag.lstrip("-")) and getattr(args, self.guiFlag.lstrip("-")):
            # Get args from gui
            self._logger.info("Opening the gui...")
            return self.parseArgsWithGui()
        else:
            # Get args from cli
            self._logger.info("Parsing cli arguments...")
            return self._parser.parse_args()

    def parseArgsWithGui(self) -> Optional[argparse.Namespace]:
        """
        Helper function that explicitly presents the gui and parses provided arguments.
        The gui flag will be ignored.

        Returns any parsed arguments.
        """
        # TODO: Startup the Gui
        gui = Interface()
        gui.run()

        # TODO: Execute this function somewhere appropriate for the gui
        return self._submitGuiArgs()

    # Private Functions
    def _addGuiArgument(self, parser: argparse.ArgumentParser):
        """
        Adds the gui Flag argument to the parser.

        parser: The parser to add the argument to.
        """
        # Add the argument
        # TODO: Let user provide the help text
        parser.add_argument(self.guiFlag, action="store_true", help="Show the gui interface")

    def _submitGuiArgs(self) -> Optional[argparse.Namespace]:
        """
        Submits the arguments from the gui.

        Returns any parsed arguments.
        """
        return None
