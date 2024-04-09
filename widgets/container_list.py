import subprocess
from rich.text import Text

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, DataTable, Log, Label, Select, Collapsible, SelectionList
from textual.reactive import reactive


class ContainerList(Static):
    """A table to display container information."""

    containers = reactive([])

    def compose(self) -> ComposeResult:
        selections = [("First", 1), ("Second", 2)]

        yield Vertical(
            Horizontal(
                Button("Refresh", id="refresh", variant="primary"),
                Select(
                    [('Running', 'up'), ('Exited', 'exited')],
                    prompt='All projects', id='select_project'
                ),
                classes="top-menu"
            ),
            DataTable(cursor_type='row', fixed_columns=1),
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Name", "Status", "Open ports", "Networks", "Log size", "CPU", "Memory", "IO")

        # self.update_interval = self.set_interval(10, self.update_containers)
        self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh":
            self.refresh_data()

    def refresh_data(self) -> None:
        """Method to update the containers attribute."""
        # self.containers = []
        try:
            cmd = "docker ps --format \"{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}\""
            result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(e.stderr)

        # log = self.query_one(Log)
        # log.clear()
        # log.write_line(result.stdout)

        new_containers = []
        for line in result.stdout.splitlines():
            cid, name, status, ports = line.split("|")
            ports = ports.split(", ")
            open_ports = []
            for _port in ports:
                if '->' in _port:
                    open_ports.append(_port)
            rich_ports = Text()
            for i, _port in enumerate(open_ports):
                rich_ports.append(_port, style="red" if '0.0.0.0:' in _port else '')
                if i < len(open_ports) - 1:
                    rich_ports.append(", ")
            new_containers.append({
                'id': cid,
                'name': name,
                'status': status,
                'open_ports': rich_ports,
            })

        self.containers = new_containers

    def watch_containers(self, containers: list[dict[str, str]]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for row in self.containers:
            table.add_row(row['name'], row['status'], row['open_ports'])
