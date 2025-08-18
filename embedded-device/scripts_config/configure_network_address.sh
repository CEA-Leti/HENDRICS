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
    echo_error "'configure_network_address.sh' script expects exactly 3 argument, but received $#."
    echo "[!] Usage: sudo $0 <path/to/output/images/sdcard.img> <adresse_IP/netmask> <MAC_address>"
    exit 1
fi


# Check if the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo_error "Script '$0' must be run as root."
   exit 1
fi


# Variable declarations
img_file="$1"
ip_address="$2"
mac_address="$3"
br_mount_dir="/mnt/eEDR_testbed/img_mount"
network_conf="etc/systemd/network/10-end0.network"


# Extract the IP address and subnet mask from the input
ip_address=$(echo "$2" | cut -d '/' -f 1)
subnet_mask=$(echo "$2" | cut -d '/' -f 2)


# Create the mount directory if it doesn't already exist
sudo mkdir -p "$br_mount_dir"


# Mount the 4th partition of the image file
br_loop=$(losetup -f --show -P "$img_file")
sudo mount -o loop "$br_loop"p4 "$br_mount_dir"
if [ $? -ne 0 ]; then
    echo_error "Unable to mount the filesystem of the sdcard.img file."
    losetup -d "$br_loop"
    exit 1
fi


# Update the configuration file with the provided IP address and subnet mask
sudo sed -i "s/Address=.*/Address=$ip_address\/$subnet_mask/" "$br_mount_dir/$network_conf"
if [ $? -ne 0 ]; then
    echo_error "Failed to update the IP address in the configuration file."
    exit 1
fi


# Update the configuration file with the provided MAC address
sudo sed -i "s/MACAddress=.*/MACAddress=$mac_address/" "$br_mount_dir/$network_conf"
if [ $? -ne 0 ]; then
    echo_error "Failed to update the MAC address in the configuration file."
    exit 1
fi


# Unmount the filesystem from the image and clean up
sudo umount -l "$br_mount_dir"
if [ $? -ne 0 ]; then
    echo_error "Unable to unmount the filesystem of the sdcard.img file."
    exit 1
fi

losetup -d "$br_loop"
sudo rmdir "$br_mount_dir"

echo_info "Status: 'configure_network_address.sh' script successfully configured the IP address and MAC address."
exit 0
