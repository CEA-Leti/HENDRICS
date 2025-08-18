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


if [ $# -ne 1 ]; then
    echo "[!] Error: 'restauration.sh' script expects exactly 1 argument, but received $#."
    echo "[!] Usage: $0 <Target IP Address>"
    exit 1
fi

OPENPLC_USERNAME="openplc"
OPENPLC_PASSWORD="openplc"
NEW_PRIVILEGED_USER="rce_openplc_user"
NEW_PRIVILEGED_PASSWORD="evil_password"

target_ip_address=$1

if ! (ping -c 1 -W 2 $target_ip_address > /dev/null 2>&1); then
	echo "[!] Error: Invalid IP address or host unreachable."
    exit 1
fi

# If the attack was initiated in automated mode, remove the created user
sshpass -p "$NEW_PRIVILEGED_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$NEW_PRIVILEGED_USER"@$target_ip_address << EOF > /dev/null 2>&1
    deluser --remove-home "$NEW_PRIVILEGED_USER" 
EOF

cd scripts/
python3 openplc_restoration.py $target_ip_address $OPENPLC_USERNAME $OPENPLC_PASSWORD

echo "[+] Restoration process complete."
