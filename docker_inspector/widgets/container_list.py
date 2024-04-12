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

    containers = reactive([])
    projects = reactive([])

    def compose(self) -> ComposeResult:

        # yield ScrollableContainer(
        #     Horizontal(
        #         Button("Refresh", id="refresh", variant="primary"),
        #         Select(
        #             [],
        #             prompt='All projects', id='select_project'
        #         ),
        #         classes="top-menu"
        #     ),
        #     DataTable(cursor_type='row', fixed_columns=1),
        #     Placeholder("TODO: Volumes", id="volumes")
        # )
        yield Vertical(
            Horizontal(
                Button("Refresh", id="refresh", variant="primary"),
                Select(
                    [],
                    prompt='All projects', id='select_project'
                ),
                classes="top-menu"
            ),
            DataTable(cursor_type='row', fixed_columns=1)
        )

        # yield Placeholder("...", id="volumes")

    def on_mount(self) -> None:
        self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh":
            self.refresh_data()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "select_project":
            self.refresh_table()

    # Сортировка при клике по заголовку
    # def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
    #     print(event)
    #     table = self.query_one(DataTable)
    #     table.sort(event.column_key)


    def refresh_data(self) -> None:
        """Method to update the containers attribute."""
        # self.containers = []
        try:
            cmd = "docker ps --format \"{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}\""
            result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(e.stderr)

        # try:
        #     cmd = 'docker stats --no-stream --format "{{.ID}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}|{{.PIDs}}"'
        #     result_stats = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # except subprocess.CalledProcessError as e:
        #     raise Exception(e.stderr)

        # containers_runtime_stats = {}
        # for line in result_stats.stdout.splitlines():
        #     container_id, cpu, mem, mem_perc, net_io, block_io, pids = line.split("|")
        #     containers_runtime_stats[container_id] = {
        #         'cpu': cpu,
        #         'mem': mem,
        #         'mem_perc': mem_perc,
        #         'net_io': net_io,
        #         'block_io': block_io,
        #         'pids': pids
        #     }

        new_containers = []
        projects = set()
        for line in result.stdout.splitlines():
            container_id, name, status, ports = line.split("|")
            try:
                cmd = f"docker inspect {container_id}"
                result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                result_js = json.loads(result.stdout)[0]
            except subprocess.CalledProcessError as e:
                raise Exception(e.stderr)

            container_info = {
                'id': container_id,
                'name': name,
                'status': status,
            }
            # container_info.update(containers_runtime_stats[container_id])

            project = result_js['Config']['Labels']['com.docker.compose.project']
            projects.add(project)
            container_info['project'] = project

            # open ports
            open_ports = []
            for inner, outer in result_js['HostConfig']['PortBindings'].items():
                if outer:
                    out_ip = outer[0]['HostIp']
                    out_port = outer[0]['HostPort']
                    if out_ip in ['0.0.0.0', '']:
                        open_ports.append(Text(f"*:{out_port}->{inner}", style="red bold"))
                    elif out_ip in ['127.0.0.1', 'localhost']:
                        open_ports.append(Text(f"l:{out_port}->{inner}", style="green"))
                    else:
                        open_ports.append(Text(f"{out_ip}:{out_port}->{inner}", style="orange"))
            container_info['open_ports'] = Text(", ").join(open_ports)

            # networks
            networks = ', '.join(result_js['NetworkSettings']['Networks'].keys())
            container_info['networks'] = networks

            # log size
            log_path = result_js['LogPath']
            if os.path.exists(log_path):
                log_size = os.path.getsize(log_path)
                container_info['log_size'] = f"{round(log_size / 1024 / 1024, 2)} Mb"
            else:
                container_info['log_size'] = 'N/A'

            #restart policy
            restart_policy = result_js['HostConfig']['RestartPolicy']['Name']
            container_info['restart_policy'] = restart_policy

            new_containers.append(container_info)

        new_containers.sort(key=lambda x: x['name'])
        self.containers = new_containers
        self.projects = sorted(projects)

    def refresh_table(self) -> None:
        select = self.query_one('#select_project', Select)
        project_filter = select.value
        table = self.query_one(DataTable)
        table.clear(columns=True)
        _columns = ["Name", "Project", "Status", "Open ports", "Networks",
                    "Log size", "Restart",
                    # "CPU %", "Memory %", "Memory", "Net IO", "Disk IO", "PIDs"
                    ]
        if project_filter != Select.BLANK:
            del _columns[1]  # remove project column
        table.add_columns(*_columns)
        for row in self.containers:
            if project_filter == Select.BLANK or row['project'] == project_filter:
                _row = [
                    row['name'], row['project'], row['status'], row['open_ports'],
                    row['networks'], row['log_size'], row['restart_policy'],
                    # row['cpu'], row['mem_perc'], row['mem'], row['net_io'], row['block_io'], row['pids']
                ]
                if project_filter != Select.BLANK:
                    del _row[1] # remove project column
                table.add_row(*_row)
        print(table.row_count + 2)
        print(len(self.containers) + 2)
        # table.styles.height = len(self.containers) + 2
        table.styles.height = 25

    def watch_containers(self, containers: list[dict[str, str]]) -> None:
        self.refresh_table()

    def watch_projects(self, projects: list[str]) -> None:
        select = self.query_one('#select_project', Select)
        select.set_options([(p, p) for p in projects])
