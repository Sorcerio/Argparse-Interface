# Argparse Interface: Wrapper
# Host wrapper for the Interface.

# MARK: Imports
import argparse
import logging
from typing import Union, Optional, Any

from .Interface import Interface
from .Logging import getLogger
from .ReturnCodes import ReturnCodes

# MARK: Classes
class Wrapper:
    """
    Automatic interface wrapper for the `argparse` module.

    Use this class to automatically handle the interface.
    """
    # Constructor
    def __init__(self,
        parser: argparse.ArgumentParser,
        guiFlag: str = "--gui",
        guiHelp: str = "Show the gui interface",
        logLevel: int = logging.INFO,
        debugUI: bool = False,
    ):
        """
        parser: The top-level `ArgumentParser` object to use in the interface.
        guiFlag: The flag to use to indicate that the gui should be shown.
        guiHelp: The help text to use for the gui flag.
        logLevel: The logging level to use.
        debugUI: If `True`, the debug elements will be shown.
        """
        # Record data
        self._parser = parser
        self.guiFlag = guiFlag
        self.guiHelp = guiHelp
        self.showDebugUI = debugUI
        self._logger = getLogger(logLevel)

        # Add the gui argument to the parser
        self._addGuiArgument(self._parser)

    # Functions
    def parseArgs(self) -> Optional[argparse.Namespace]:
        """
        Parses the arguments using the method defined by the cli flags.
        Will open the gui if prompted.
        Otherwise, will parse the cli arguments as normal.

        Returns any parsed arguments as an `argparse.Namespace` object or `None` if the gui was quit without submitting.
        """
        # Create gui argument parser
        guiArgParser = argparse.ArgumentParser(add_help=False)
        self._addGuiArgument(guiArgParser)

        # Parse the cli args
        args = guiArgParser.parse_known_args()[0]

        # Check if the gui flag is present
        if hasattr(args, self.guiFlag.lstrip("-")) and getattr(args, self.guiFlag.lstrip("-")):
            # Get args from gui
            self._logger.info("Starting the gui.")
            return self.parseArgsWithGui()
        else:
            # Get args from cli
            self._logger.info("Parsing cli arguments.")
            return self._parser.parse_args()

    def parseArgsWithGui(self) -> Optional[argparse.Namespace]:
        """
        Explicitly presents the gui (as opposed to the cli or gui) and parses provided arguments.
        The gui flag will be ignored.

        Returns any parsed arguments as an `argparse.Namespace` object or `None` if the gui was quit without submitting.
        """
        # Startup the Gui
        gui = Interface(
            self._parser,
            self.guiFlag,
            title=self._parser.prog,
            subTitle=self._parser.description or Interface.SUB_TITLE,
        )
        returnCode: ReturnCodes = gui.run()

        # Check result
        if returnCode == ReturnCodes.QUIT:
            # Cancelled
            self._logger.info("Quit from the gui.")
            return None
        elif returnCode == ReturnCodes.SUBMIT:
            # Submitted
            self._logger.info("Parsed gui arguments.")
            return gui.getArgs()
        else:
            # Unknown
            self._logger.warning(f"Unexpected return code: {returnCode}")
            return None

    # Private Functions
    def _addGuiArgument(self, parser: argparse.ArgumentParser):
        """
        Adds the gui Flag argument to the parser.

        parser: The parser to add the argument to.
        """
        # Add the argument
        parser.add_argument(self.guiFlag, action="store_true", help=self.guiHelp)
