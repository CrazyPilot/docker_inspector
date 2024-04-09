from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, DataTable, Log, Label
from textual.reactive import reactive

from .widgets.container_list import ContainerList


class TestScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(Static("Hello, world!"))


class DockerInspectorApp(App):
    TITLE = "Docker Inspector"
    CSS_PATH = 'styles/main.css'
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ContainerList()

    def action_refresh(self) -> None:
        """An action to refresh the container list."""
        container_list = self.query_one(ContainerList)
        container_list.refresh_data()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


def run():
    app = DockerInspectorApp()
    app.run()


if __name__ == "__main__":
    run()