from textual.app import  ComposeResult
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, DataTable, Log, Label, Select, Collapsible, SelectionList, Placeholder
from textual.reactive import reactive


class VolumeList(Static):
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

    def refresh_data(self, volumes, filter_project) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        _columns = ["Name", "Project", "Container"]
        if filter_project:
            del _columns[1]  # remove project column
        table.add_columns(*_columns)
        for row in volumes:
            if not filter_project or filter_project in row['projects']:
                _row = [
                    row['name'], ', '.join(row['projects']), ', '.join(row['containers'])
                ]
                if filter_project:
                    del _row[1]  # remove project column
                table.add_row(*_row)

