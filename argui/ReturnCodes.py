# Argparse Interface: Return Codes
# Return codes for the GUI interface.

# MARK: Imports
from enum import Enum

# MARK: Enums
class ReturnCodes(Enum):
    """
    Return codes for the GUI interface.
    """
    SUBMIT="submit"
    QUIT="quit"
