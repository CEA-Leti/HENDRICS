#!/bin/bash
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


if [ $# -ne 2 ]; then
    echo "[!] Error: 'restauration.sh' script expects exactly 2 argument, but received $#."
    echo "[!] Usage: $0 <PLC IP Address> <Physical Process IP Address>"
    exit 1
fi

plc_ip_address=$1
physical_process_ip_address=$2

pid_ettercap=$(pgrep ettercap)
if [ -n "$pid_ettercap" ]; then
    echo "[+] Ettercap is still running. Killing process with PID: $pid_ettercap"
    kill -9 $pid_ettercap
fi

if ! (ping -c 1 -W 2 $plc_ip_address > /dev/null 2>&1); then
	echo "[!] Error: Invalid PLC IP address or host unreachable."
    exit 1
fi

echo "[+] Stopping OpenPLC script."
python3 ./scripts/PLCop.py $plc_ip_address stop_plc >/dev/null

echo "[+] Restarting the physical processes."
if ! (ping -c 1 -W 2 $physical_process_ip_address > /dev/null 2>&1); then
	echo "[!] Error: Invalid physical process IP address or host unreachable."
    exit 1
fi

curl -s "http://$physical_process_ip_address:9000/restart_simulator"
curl -s "http://$physical_process_ip_address:9000/restart_modbus"

echo "[+] Restarting OpenPLC script."
python3 ./scripts/PLCop.py $plc_ip_address start_plc >/dev/null

echo "[+] Restoration process complete."