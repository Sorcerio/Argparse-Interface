# Argparse Interface: Interface
# Automatic interface for the `argparse` module.

# MARK: Imports
from textual.app import App, ComposeResult
from textual.widgets import Welcome

# MARK: Classes
class Interface(App):
    """
    Automatic interface for the `argparse` module.

    This class is the interface runner for the module.
    Use `Wrapper` to automatically handle the interface.
    """
    # Functions
    def compose(self) -> ComposeResult:
        yield Welcome()

    def on_button_pressed(self) -> None:
        self.exit()
