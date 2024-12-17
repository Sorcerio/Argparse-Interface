# Argparse Interface: Parser Group
# A utility object that represents an `argparse.ArgumentParser` group in a more accessible way.

# MARK: Imports
import uuid
import argparse
from typing import Optional, Iterable

# MARK: Classes
class ParserGroup:
    """
    A utility object that represents an `argparse.ArgumentParser` group in a more accessible way.
    """
    # Constructor
    def __init__(self,
        isExclusive: bool,
        title: Optional[str] = None,
        reqActions: Optional[Iterable[argparse.Action]] = [],
        optActions: Optional[Iterable[argparse.Action]] = []
    ):
        """
        isExclusive: If the group is a mutually exclusive choice group.
        title: The title of the group.
        reqActions: The required actions of the group.
        optActions: The optional actions of the group.
        """
        # Set title
        if title and (len(title.strip()) > 0):
            self.title = title.strip()
            self.isUuidTitle = False
        else:
            self.title = str(uuid.uuid4())
            self.isUuidTitle = True

        # Set data
        self.isExclusive = isExclusive
        self.reqActions = reqActions
        self.optActions = optActions

    # Python Functions
    def __str__(self) -> str:
        params = [f"{key}={value}" for key, value in self.__dict__.items()]
        return f"ParserGroup({', '.join(params)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return hash(self.__str__())

    # Functions
    def allActions(self) -> Iterable[argparse.Action]:
        """
        Returns all actions of the group.
        """
        return (self.reqActions + self.optActions)