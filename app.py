import subprocess
from rich.text import Text

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Header, Footer, Button, Static, DataTable, Log, Label
from textual.reactive import reactive

from widgets.container_list import ContainerList


CAPTION = """
  _____             _               _____                           _             
 |  __ \           | |             |_   _|                         | |            
 | |  | | ___   ___| | _____ _ __    | |  _ __  ___ _ __   ___  ___| |_ ___  _ __ 
 | |  | |/ _ \ / __| |/ / _ \ '__|   | | | '_ \/ __| '_ \ / _ \/ __| __/ _ \| '__|
 | |__| | (_) | (__|   <  __/ |     _| |_| | | \__ \ |_) |  __/ (__| || (_) | |   
 |_____/ \___/ \___|_|\_\___|_|    |_____|_| |_|___/ .__/ \___|\___|\__\___/|_|   
                                                   | |                            
                                                   |_|                            
"""

class TestScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(Static("Hello, world!"))


class DockerInspectorApp(App):
    TITLE = "Docker Inspector"
    CSS_PATH = 'styles/main.tcss'
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(
            Label(CAPTION),
            ContainerList()
        )

    def action_refresh(self) -> None:
        """An action to refresh the container list."""
        container_list = self.query_one(ContainerList)
        container_list.refresh_data()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = DockerInspectorApp()
    app.run()