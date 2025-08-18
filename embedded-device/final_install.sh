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


# /!\ The following dependencies are required to ensure the proper execution of this script:
# linux-tools-common, linux-tools-<kernel_version>, pahole, sshpass, clang, llvm


# Check if the number of arguments passed to the script is exactly four
if [ $# -ne 3 ]; then
    echo_error "'final_install.sh' script expects exactly 3 argument, but received $#."
    echo "[!] Usage: $0 <Target IP Address> <Root Username> <Root Password>"
    exit 1
fi


# Variable declarations
target_ip_address=$1
ssh_user=$2
ssh_password=$3

SCRIPTDIR="$(realpath "$(dirname "$0")")"


# Execute the OpenPLC installation script
cd "$SCRIPTDIR/scripts_config"
echo_info "Running 'configure_OpenPLC.sh' to install OpenPLC."
./configure_OpenPLC.sh "$target_ip_address" "$ssh_user" "$ssh_password"  
if [ $? -ne 0 ]; then
    echo_error "Failed to execute 'configure_OpenPLC.sh'."
    exit 1
fi


# Execute the boopkit installation script
echo_info "Running 'install_boopkit.sh' to install Boopkit."
./install_boopkit.sh "$SCRIPTDIR/buildroot/output/host/bin" "$target_ip_address" "$ssh_user" "$ssh_password"
if [ $? -ne 0 ]; then
    echo_error "Failed to execute 'install_boopkit.sh'."
    exit 1
fi


echo_info "OpenPLC installation completed successfully."
exit 0
