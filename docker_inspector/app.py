import subprocess
from rich.text import Text
import json
import os

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal
from textual.widgets import Header, Footer, Button, DataTable, Log, Label, TabbedContent, TabPane, Placeholder, Select
from textual.reactive import reactive

from .widgets.container_list import ContainerList
from .widgets.volume_list import VolumeList
from .utils.get_info import get_info


# class TestScreen(Screen):
#     def compose(self) -> ComposeResult:
#         yield Header()
#         yield Footer()
#         yield ScrollableContainer(Static("Hello, world!"))


class DockerInspectorApp(App):
    TITLE = "Docker Inspector"
    CSS_PATH = 'styles/main.css'
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    projects = reactive([])
    containers = reactive([])
    volumes = reactive([])
    filter_project = reactive(None)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Horizontal(
            Button("Refresh", id="refresh", variant="primary"),
            Select(
                [],
                prompt='All projects', id='select_project'
            ),
            id="top-menu"
        )
        with TabbedContent():
            with TabPane("Containers"):
                yield ContainerList()
            with TabPane("Volumes"):
                # yield Placeholder("Volumes", id="volumes")
                yield VolumeList()

    def action_refresh(self) -> None:
        self.projects, self.containers, self.volumes = get_info()
        print(self.volumes)

        select = self.query_one('#select_project', Select)
        select.set_options([(p, p) for p in self.projects])

        container_list = self.query_one(ContainerList)
        container_list.refresh_data(self.containers, self.filter_project)

        volume_list = self.query_one(VolumeList)
        volume_list.refresh_data(self.volumes, self.filter_project)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_mount(self) -> None:
        self.action_refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh":
            self.action_refresh()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "select_project":
            self.filter_project = event.select.value if event.select.value != Select.BLANK else None

            container_list = self.query_one(ContainerList)
            container_list.refresh_data(self.containers, self.filter_project)

            volume_list = self.query_one(VolumeList)
            volume_list.refresh_data(self.volumes, self.filter_project)


def run():
    app = DockerInspectorApp()
    app.run()


if __name__ == "__main__":
    run()