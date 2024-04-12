import subprocess
from rich.text import Text
import json
import os

from textual import log
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, DataTable, Log, Label, Select, Collapsible, SelectionList, Placeholder
from textual.reactive import reactive


class ContainerList(Static):
    """A table to display container information."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            DataTable(cursor_type='row', fixed_columns=1)
        )

    # Сортировка при клике по заголовку
    # def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
    #     print(event)
    #     table = self.query_one(DataTable)
    #     table.sort(event.column_key)

    def refresh_data(self, containers, filter_project) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        _columns = ["Name", "Project", "Status", "Open ports", "Networks",
                    "Log size", "Restart",
                    # "CPU %", "Memory %", "Memory", "Net IO", "Disk IO", "PIDs"
                    ]
        if filter_project:
            del _columns[1]  # remove project column
        table.add_columns(*_columns)
        for row in containers:
            if not filter_project or row['project'] == filter_project:
                _row = [
                    row['name'], row['project'], row['status'], row['open_ports'],
                    row['networks'], row['log_size'], row['restart_policy'],
                    # row['cpu'], row['mem_perc'], row['mem'], row['net_io'], row['block_io'], row['pids']
                ]
                if filter_project:
                    del _row[1]  # remove project column
                table.add_row(*_row)

