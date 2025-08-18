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


# Functions to print error and informational messages
RED="\e[31m"
GREEN="\e[32m"
RESET="\e[0m"

function echo_info {
    local message="$1"
    echo -e "${GREEN}[+] ${message}${RESET}"
}
function echo_error {
    local message="$1"
    echo -e "${RED}[!] Error: ${message}${RESET}" 1>&2
}


# Check if the number of arguments passed to the script is exactly three
if [ $# -ne 3 ]; then
    echo_error "'configure_OpenPLC.sh' script expects exactly 3 argument, but received $#."
    echo "[!] Usage: sudo $0 <ip address of target> <ssh username> <ssh password>"
    exit 1
fi


# Testing SSH connection
# Note: The options "StrictHostKeyChecking=no" and "UserKnownHostsFile=/dev/null" are used to bypass host key verification during connection.
# These options prevent any manual intervention from the user, such as adding or removing the host's public key from the known hosts file.
# The goal is to simplify the installation process as much as possible.
echo_info "Testing SSH connection ..."
sshpass -p "$3" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$2@$1"<<EOF
    ls 
    echo "Status command on remote machine : \$?"
EOF
ssh_exit_code=$?
if [ $ssh_exit_code -ne 0 ]; then
    echo_error "Failed to establish SSH connection. Please ensure the host is reachable and that the credentials are valid."
    exit 1
fi


echo_info "The SSH connexion is established."
echo_info "Updating date on the target machine."

sshpass -p "$3" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$2@$1" date "$(date +"%m%d%H%M%Y")"
if [[ $? -ne 0 ]]; then 
    echo_error "Failed to update the date on the target machine."
    exit 1
fi


# Execute the following commands on the remote machine
echo_info "We are going to install the python virtual environment and packages, this takes generally 10 minutes."
sshpass -p "$3" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$2@$1"<<EOF
    cd /etc 
    python -m venv .venv 
    echo $? 
    source .venv/bin/activate
    echo $? 
    python -m pip install --no-index --find-links=/etc/custom_libs flask 
    echo $?
    python -m pip install --no-index --find-links=/etc/custom_libs Flask-Login
    echo $?
    python -m pip install --no-index --find-links=/etc/custom_libs six
    echo $?
    python -m pip install --no-index --find-links=/etc/custom_libs wheel
    echo $?
    python -m pip install --no-index --find-links=/etc/custom_libs pymodbus
    echo $?
    deactivate 
    echo $?
    systemctl daemon-reload
    echo $?
    systemctl enable openplc.service 
    echo $?
    cd /etc/OpenPLC_v3/webserver/scripts
    ./change_hardware_layer.sh blank_linux 
    cd /etc/OpenPLC_v3/webserver
    echo "blank_program.st" > active_program
    echo $?
    systemctl start openplc.service
    echo $?
    systemctl status openplc.service 
    echo $? 
EOF


echo_info "Status: 'configure_OpenPLC.sh' script successfully installed OpenPLC."
exit 0