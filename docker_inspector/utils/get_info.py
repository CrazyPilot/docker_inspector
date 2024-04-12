import subprocess
from rich.text import Text
import json
import os


def get_info():
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

    containers = []
    volume_to_containers = {}  # volume name -> list of containers
    volume_to_projects = {}  # volume name -> list of projects
    projects = set()
    for line in result.stdout.splitlines():
        container_id, name, status, ports = line.split("|")
        try:
            cmd = f"docker inspect {container_id}"
            result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    shell=True)
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

        # Volumes
        for _mount in result_js['Mounts']:
            if _mount['Type'] == 'volume':
                volume_to_containers.setdefault(_mount['Name'], []).append(name)
                volume_to_projects.setdefault(_mount['Name'], []).append(project)

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

        # restart policy
        restart_policy = result_js['HostConfig']['RestartPolicy']['Name']
        container_info['restart_policy'] = restart_policy

        containers.append(container_info)

    containers.sort(key=lambda x: x['name'])

    #######
    volumes = []
    try:
        cmd = "docker volume ls --format \"{{.Name}}\""
        result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)
    for line in result.stdout.splitlines():
        volume_info = {
            'name': line,
            'containers': volume_to_containers.get(line, []),
            'projects': volume_to_projects.get(line, [])
        }
        volumes.append(volume_info)

    return sorted(projects), containers, volumes