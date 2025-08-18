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


if [ $# -ne 1 ]; then
    echo "[!] Error: 'restauration.sh' script expects exactly 1 argument, but received $#."
    echo "[!] Usage: $0 <Target IP Address>"
    exit 1
fi

ROOT_USERNAME=root
ROOT_PASSWORD=root
REDIS_PASSWORD=coconut

target_ip_address=$1

if ! (ping -c 1 -W 2 $target_ip_address > /dev/null 2>&1); then
	echo "[!] Error: Invalid IP address or host unreachable."
    exit 1
fi

echo "[+] Shutting down the Redis service."
redis-cli -h $1 -a "$REDIS_PASSWORD" SHUTDOWN

echo "[+] Restarting SenseHAT services (MQTT publisher, Sensor webserver, Redis, Sensor Manager, and LED manager)."
sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$ROOT_USERNAME@$target_ip_address" << EOF 
    systemctl restart sensehat.service
EOF

sleep 10  # Pause to ensure the Sense HAT services has enough time to fully restart
echo "[+] Restoration process complete."