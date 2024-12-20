# Export DOM
# Exports the Textual DOM that is currently displayed.

# MARK: Imports
import json
from pathlib import Path

from textual.widget import Widget

# MARK: Functions
def mapDOM(widget: Widget) -> dict[str, dict]:
    """
    Maps the DOM of the screen to a dictionary.

    widget: The root Textual `Widget` to start mapping from. Use `self.screen` from an `App` object.
    """
    # Setup data
    widgetClass = widget.__class__.__name__
    widgetData = {
        widgetClass: {
            "_id": getattr(widget, "id", None),
            "_classes": [str(c) for c in getattr(widget, "classes", [])],
        }
    }

    # Process the children
    for child in getattr(widget, 'children', []):
        widgetData[widgetClass].update(mapDOM(child))

    return widgetData

def exportDOM(widget: Widget, outfile: str = "./dom.json") -> None:
    """
    Maps the DOM of the screen to a dictionary and exports it to a JSON file.

    widget: The root Textual `Widget` to start mapping from. Use `self.screen` from an `App` object.
    outfile: The file to export the DOM to.
    """
    # Export the DOM
    with open(Path(outfile).resolve(), "w") as file:
        json.dump(mapDOM(widget), file, indent=4)
