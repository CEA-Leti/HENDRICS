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


# Script to install gdb on the STM32MP1

# Check if the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo "[!] This script must be run as root to mount the required file system." 1>&2
   echo "[!] Usage: sudo $0 <Target IP Address>"
   exit 1
fi

# Check if the number of arguments passed to the script is exactly four
if [ $# -ne 1 ]; then
    echo "[!] 'install_gdb.sh' script expects exactly 1 argument, but received $#."
    echo "[!] Usage: sudo $0 <Target IP Address>"
    exit 1
fi

# Variables for connection and file paths
ip_address=$1
username="root"
password="root"
rpi_mount_dir="/mnt/raspberry-gdb"
raspbi_image_dir="$(realpath "$(dirname "$0")")/2023-10-10-raspios-bookworm-armhf.img"

# Function to unmount the Raspberry Pi image and clean up
unmount_rpi_image(){
  echo "Unmounting the Raspberry Pi image..."
  umount -l "$rpi_mount_dir"
  losetup -d "$raspbi_loop"
  rmdir  "$rpi_mount_dir"
}


# Download Raspberry Pi image file
echo "[+] Downloading Raspberry Pi image file."
rm -f ./2023-10-10-raspios-bookworm-armhf.img.xz
wget https://downloads.raspberrypi.com/raspios_armhf/images/raspios_armhf-2023-10-10/2023-10-10-raspios-bookworm-armhf.img.xz
if [ $? -ne 0 ]; then
    echo "Error: Failed to download Raspberry Pi image file."
    exit 1
fi


# Unzip the downloaded .img file
echo "[+] Unzipping the .img file."
xz -d -f ./2023-10-10-raspios-bookworm-armhf.img.xz
if [ $? -ne 0 ]; then
    echo "Error: Failed to unzip the .img file."
    exit 1
fi


# Mount the 2th partition of the raspberry Pi image file
mkdir -p "$rpi_mount_dir"
echo "[+] Mounting the partition of the Raspberry Pi image..."
raspbi_loop=$(losetup -f --show -P "$raspbi_image_dir")
sudo mount -o loop "$raspbi_loop"p2 "$rpi_mount_dir"
if [ $? -ne 0 ]; then
    echo "Error: Unable to mount the filesystem of the raspberry Pi image file."
    losetup -d "$raspbi_loop"
    exit 1
fi


# Transfer the gdb binary from the raspberry Pi image to the STM32MP1
cd "$rpi_mount_dir/bin"
echo "[+] Transfering the gdb binary to the STM32MP1"
sshpass -p "$password" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "gdb" "$username@$ip_address:/bin"
if [[ $? -ne 0 ]]; then 
    echo "Error: Failed to transfer the gdb binary to the target machine."
    unmount_rpi_image
    exit 1
fi


# Transfer necessary gdb libraries from the raspberry Pi image to the STM32MP1
cd "$rpi_mount_dir/lib/arm-linux-gnueabihf"
echo "[+] Transfering the gdb libraries to the STM32MP1"
libs=("libncursesw.so.6" "libtinfo.so.6" "liblzma.so.5" "libbabeltrace.so.1" "libbabeltrace-ctf.so.1" "libsource-highlight.so.4" "libxxhash.so.0" "libdebuginfod.so.1" "libboost_regex.so.1.74.0" "libcurl-gnutls.so.4" "libicui18n.so.72" "libicuuc.so.72" "libnghttp2.so.14" "libidn2.so.0" "librtmp.so.1" "libssh2.so.1" "libpsl.so.5" "libnettle.so.8" "libgnutls.so.30" "libgssapi_krb5.so.2" "libgssapi_krb5.so.2" "libldap-2.5.so.0" "liblber-2.5.so.0" "libbrotlidec.so.1" "libicudata.so.72" "libunistring.so.2" "libhogweed.so.6" "libcrypto.so.3" "libp11-kit.so.0" "libtasn1.so.6" "libkrb5.so.3" "libk5crypto.so.3" "libcom_err.so.2" "libkrb5support.so.0" "libsasl2.so.2" "libbrotlicommon.so.1" "libkeyutils.so.1")
for lib in "${libs[@]}"; do
  sshpass -p "$password" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$lib" "$username@$ip_address:/lib"
  if [[ $? -ne 0 ]]; then 
    echo "Error: Failed to transfer the $lib library to the target machine."
    unmount_rpi_image
    exit 1
  fi
done


# Transfer the GDB Python libraries to the STM32MP1
echo "[+] Transferring the GDB Python libraries to the STM32MP1"
sshpass -p "$password" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -r "$rpi_mount_dir/usr/share/gdb" "$username@$ip_address:/usr/share/gdb"
if [[ $? -ne 0 ]]; then 
    echo "Error: Failed to transfer the Python libraries to the target machine."
    unmount_rpi_image
    exit 1
fi

unmount_rpi_image
echo "Successfully transferred gdb and libraries to STM32MP1."
exit 0