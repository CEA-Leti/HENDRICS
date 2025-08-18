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


# Synchronize the system date and time on the target device.
# This is often required for OpenPLC to function properly, as it may prevent login or communication if the system time is not up to date.

# Check if the number of arguments passed to the script is exactly three
if [ $# -ne 3 ]; then
    echo "[!] Error: 'update_timedate.sh' script expects exactly 3 argument, but received $#." 1>&2
    echo "[!] Usage: $0 <Target IP Address> <SSH Username> <SSH Password>"
    exit 1
fi

TARGET_IP=$1
SSH_USERNAME=$2
SSH_PASSWORD=$3
CURRENT_DATE=$(date +"%m%d%H%M%Y")

sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$SSH_USERNAME"@"$TARGET_IP" date "$CURRENT_DATE"
if [ $? -ne 0 ]; then 
    echo "[!] Error: Failed to update the date on the target device ($TARGET_IP)." 1>&2
    exit 1
else
    echo "Successfully updated the date on the target device ($TARGET_IP) to $CURRENT_DATE."
fi