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

target_ip_address=$1

if ! (ping -c 1 -W 2 $target_ip_address > /dev/null 2>&1); then
	echo "[!] Error: Invalid IP address or host unreachable."
    exit 1
fi

echo "[+] Restoring the backup.sh script on the target system."
sshpass -p "$ROOT_PASSWORD" scp -O -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR scripts/default_backup.sh "$ROOT_USERNAME"@$target_ip_address:/etc/backup.sh

echo "[+] Restoration process complete."