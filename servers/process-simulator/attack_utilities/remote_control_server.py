# Copyright (C) 2025 CEA - All Rights Reserved
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import time

import paramiko
import docker

HOST = '0.0.0.0'
PORT = 9000

DOCKER_CLIENT = docker.DockerClient(base_url='unix://var/run/docker.sock')


def run_ssh_command(ip_address: str, username: str, password: str):
    """
    Establish an SSH connection to the specified IP address and run a test command.
    This is used to automate the `SSH_AiTM` attack scenario by triggering an SSH connection from the SCADA server to the PLC.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(
            hostname=ip_address,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False
        )

        command_list = ["cd /usr/bin/hendrics/", "ls -l", "tail -n 10 STM32_python.log"]
        for cmd in command_list:
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            stdout.channel.recv_exit_status()

            print("STDOUT:", stdout.read().decode())
            print("STDERR:", stderr.read().decode())

            time.sleep(1)

    except Exception as e:
        print(f'SSH connection failed: {e}')

    finally:
        ssh_client.close()

    
# HTTP server providing remote control endpoints for managing attack-related services
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):

        # Endpoint to remotely restart the physical process simulator container (used for restoring the Modbus_AiTM attack)
        if self.path == '/restart_modbus':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Restarting the Modbus container...\n")
            DOCKER_CLIENT.containers.get("modbus").restart()

        elif self.path == '/restart_redis':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Restarting the Redis container...\n")
            DOCKER_CLIENT.containers.get("redis").restart()

        elif self.path == '/restart_simulator':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Restarting the simulator container...\n")
            DOCKER_CLIENT.containers.get("simulator").restart()

        # Endpoint to remotely trigger an SSH connection from the SCADA server to the PLC (used for testing the SSH_AiTM attack)
        elif self.path.startswith('/ssh_connection'):
            self.send_response(200)
            self.end_headers()

            parsed_query = urlparse(self.path)
            query_params = parse_qs(parsed_query.query)

            ip_address = query_params.get('ip_address')[0]
            username = query_params.get("username")[0]
            password = query_params.get("password")[0]
            run_ssh_command(ip_address, username, password)

            self.wfile.write(b"SSH request sent to the target.")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint not found. Use /restart_modbus, /restart_redis, /restart_simulator or /ssh_connection.")

server = HTTPServer((HOST, PORT), Handler)
print(f"Restart server running on http://{HOST}:{PORT}/")
server.serve_forever()


