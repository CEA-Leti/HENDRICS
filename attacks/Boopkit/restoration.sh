#! /bin/bash 
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
    echo "[!] Usage: $0 <Target IP Address> <Root Username>"
    echo "[!] Note: The username must be the same as the one used during the attack."
    exit 1
fi

ROOT_USERNAME=root
ROOT_PASSWORD=root

target_ip_address=$1
attack_username=$2


if ! (ping -c 1 -W 2 $target_ip_address > /dev/null 2>&1); then
	echo "[!] Error: Invalid IP address or host unreachable."
    exit 1
fi

echo "[+] Stopping Boopkit on the target device."
sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$ROOT_USERNAME"@$target_ip_address << EOF 
    ps aux | grep "boopkit" | grep -v grep | awk '{print \$1}' | xargs kill -9
EOF

# If Boopkit was lauched by a user other than 'root', remove the '.boopkit' directory from that user's home folder
if [ "$attack_username" != "root" ]; then
	sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$ROOT_USERNAME"@$target_ip_address "rm -rf /home/$attack_username/.boopkit"
fi

echo "[+] Restoration process complete."
