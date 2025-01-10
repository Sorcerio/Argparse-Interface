# Argparse Interface: Utilities
# General functions and utilities for Argparse Interface.

# MARK: Imports
import re
from typing import Optional, Union, Iterable

# MARK: Functions
def toTitleCase(s: str) -> str:
    """
    Converts a string to title case.
    """
    return " ".join([w.capitalize() for w in s.split(" ")])

def splitCamelCase(s: str) -> str:
    """
    Splits a camel case string into words.
    """
    return " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split())

def splitSnakeCase(s: str) -> str:
    """
    Splits a snake case string into words.
    """
    return " ".join([w for w in s.split("_")])

def codeStrToTitle(s: str) -> str:
    """
    Converts a code stlye string (camelCase or snake_case) to a title case string.
    """
    return toTitleCase(splitCamelCase(splitSnakeCase(s)))

def typedStringToValue(s: str, inputType: str) -> Optional[Union[str, int, float]]:
    """
    Converts a typed input string into an `int`, `float`, the `s` string, or `None`.

    s: The string to convert.
    inputType: The type of input to convert to.

    Returns the converted value.
    """
    try:
        if inputType == "integer":
            return int(s)
        elif inputType == "number":
            return float(s)
        else:
            return s
    except ValueError:
        return None

def limitString(
    s: str,
    maxChars: int,
    postfix: str = "...",
    trimRight: bool = True
) -> str:
    """
    Limits a string to a certain number of characters, adding a postfix if the string is longer than the limit.
    Takes the length of the postfix into account.

    s: The string to limit.
    maxChars: The maximum number of characters the string should have.
    postfix: The postfix to add to the string if it is longer than the limit.
    trimRight: If `True`, the postfix will be added to the right side of the string like "Hello...". If `False`, the postfix will be added to the left side of the string like "...World".

    Returns a string with a length less than or equal to `maxChars`.
    """
    # Check if it's even a string
    if not isinstance(s, str):
        raise ValueError("`s` must be a string.")

    # Check if it's within range
    if len(s) <= maxChars:
        return s

    # Check the side to cut
    if trimRight:
        # Trim the right side
        return s[:maxChars - len(postfix) + 1] + postfix
    else:
        # Trim the left side
        return postfix + s[-(maxChars - len(postfix) + 1):]

def joinOptions(items: Iterable[str], conj: str, sep: str = ", ") -> str:
    """
    Joins the given `items` like using `'<sep>'.join(items)` but adds the given conjunction before the last item.

    items: The items to join.
    conj: The conjunction to add before the last item. Usually "or" or "and".
    sep: The separator to use between items. Usually ", ".

    Returns the joined string.
    """
    # Check if there are items
    if not items:
        return ""

    # Join based on length
    itemLen = len(items)
    if itemLen == 1:
        return items[0]
    elif itemLen == 2:
        return f"{items[0]} {conj} {items[1]}"
    else:
        return f"{sep.join(items[:-1])}{sep}{conj} {items[-1]}"
