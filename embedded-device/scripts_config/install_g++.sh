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


# Check if the number of arguments passed to the script is exactly two
if [ $# -ne 2 ]; then
    echo_error "'install_g++.sh' script expects exactly 2 argument, but received $#."
    echo "[!] Usage: sudo $0 </path/to/buildroot/output/images/sdcard.img> </path/to/2023-10-10-raspios-bookworm-armhf.img>"
    exit 1
fi


# Check if the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo_error "Script '$0' must be run as root."
   exit 1
fi


# Variable declarations
SCRIPTDIR="$(realpath "$(dirname "$0")")"
br_image_dir="$1"
raspbi_image_dir="$2"
rpi_mount_dir="/mnt/eEDR_testbed/rpi"
br_mount_dir="/mnt/eEDR_testbed/br"


# Mount the 2th partition of the raspberry Pi image file
mkdir -p "$rpi_mount_dir"
echo_info "Mounting the partition of the Raspberry Pi image..."
raspbi_loop=$(losetup -f --show -P "$raspbi_image_dir")
sudo mount -o loop "$raspbi_loop"p2 "$rpi_mount_dir"
if [ $? -ne 0 ]; then
    echo_error "Unable to mount the filesystem of the raspberry Pi image file."
    losetup -d "$raspbi_loop"
    exit 1
fi


# Mount the 4th partition of the image compiled with Buildroot
mkdir -p "$br_mount_dir"
echo_info "Mountting the partition of the OS image compiled with Buildroot (sdcard.img)..."
br_loop=$(losetup -f --show -P "$br_image_dir")
sudo mount -o loop "$br_loop"p4 "$br_mount_dir"
if [ $? -ne 0 ]; then
    echo_error "Unable to mount the filesystem of the sdcard.img file."
    losetup -d "$br_loop"
    losetup -d "$raspbi_loop"
    exit 1
fi


# Install g++ executable
echo_info "Installing g++ executable..."
cp "$rpi_mount_dir"/bin/arm-linux-gnueabihf-g++-12 "$br_mount_dir"/bin

cd "$br_mount_dir"/bin

ln -s arm-linux-gnueabihf-g++-12 g++-12
ln -s g++-12 g++
ln -s g++-12 arm-linux-gnueabihf-g++

cd "$SCRIPTDIR"


# Install cc1plus executable
echo_info "Installing cc1plus executable..."

cp -r "$rpi_mount_dir"/usr/lib/gcc "$br_mount_dir"/lib > /dev/null
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libasan.so.8.0.0 "$br_mount_dir"/usr/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libcc1.so.0.0.0 "$br_mount_dir"/usr/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libgomp.so.1.0.0 "$br_mount_dir"/usr/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libstdc++.so.6.0.30 "$br_mount_dir"/usr/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libubsan.so.1.0.0 "$br_mount_dir"/usr/lib

cd "$br_mount_dir"/usr/lib

ln -s libasan.so.8.0.0 libasan.so.8
ln -s libcc1.so.0.0.0 libcc1.so.0
ln -s libgomp.so.1.0.0 libgomp.so.1
rm libstdc++.so
rm libstdc++.so.6
rm libstdc++.so.6.0.29
ln -s libstdc++.so.6.0.30 libstdc++.so.6
ln -s libstdc++.so.6.0.30 libstdc++.so
ln -s libubsan.so.1.0.0 libubsan.so.1

cd "$SCRIPTDIR"

cd "$br_mount_dir"/lib/gcc/arm-linux-gnueabihf/12

rm libasan.so
rm libatomic.so
rm libubsan.so
rm libcc1.so
rm libgomp.so
rm libstdc++.so

ln -s /usr/lib/libasan.so.8 libasan.so
ln -s /usr/lib/libatomic.so.1 libatomic.so
ln -s /usr/lib/libcc1.so.0 libcc1.so
ln -s /usr/lib/libgomp.so.1 libgomp.so
ln -s /usr/lib/libstdc++.so.6 libstdc++.so
ln -s /usr/lib/libubsan.so.1 libubsan.so

cd "$SCRIPTDIR"


# Install cc1plus dependencies
echo_info "Installing cc1plus dependencies..."

cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libisl.so.23.2.0 "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libmpc.so.3.3.1 "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libmpfr.so.6.2.0  "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libzstd.so.1.5.4 "$br_mount_dir"/lib

cd "$br_mount_dir"/lib

ln -s libisl.so.23.2.0 libisl.so.23
ln -s libmpc.so.3.3.1 libmpc.so.3 
rm libmpfr.so 
rm libmpfr.so.6
rm libmpfr.so.6.1.1
ln -s libmpfr.so.6.2.0 libmpfr.so.6 
ln -s libmpfr.so.6.2.0 libmpfr.so
ln -s libzstd.so.1.5.4 libzstd.so.1
ln -s libm.so.6 libm.so 
ln -s libc.so.6 libc.so

cd "$SCRIPTDIR"

cp "$rpi_mount_dir"/usr/lib/arm-linux-gnueabihf/libarmmem-v7l.so "$br_mount_dir"/usr/lib

cp -r "$rpi_mount_dir"/usr/include "$br_mount_dir"/usr


# Install 'as' executable
echo_info "Installing 'as' executable..."

cp "$rpi_mount_dir"/bin/as "$br_mount_dir"/bin
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libbfd-2.40-system.so "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libsframe.so.0 "$br_mount_dir"/lib


# Install ld executable 
echo_info "Installing ld executable..."

cp "$rpi_mount_dir"/bin/ld "$br_mount_dir"/bin

cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libctf.so.0  "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libjansson.so.4  "$br_mount_dir"/lib


# Retrive global configurations files needed by the toolchain
echo_info "Retrieving global files needed by the toolchain..."

cp "$rpi_mount_dir"/usr/lib/arm-linux-gnueabihf/crt1.o "$br_mount_dir"/usr/lib
cp "$rpi_mount_dir"/usr/lib/arm-linux-gnueabihf/crti.o "$br_mount_dir"/usr/lib
cp "$rpi_mount_dir"/usr/lib/arm-linux-gnueabihf/crtn.o "$br_mount_dir"/usr/lib


# Retrieve specific files needed by OpenPLC compilation
echo_info "Retrieving specific files needed by OpenPLC compilation..."

cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libc.a "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libc_nonshared.a "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libpthread.a "$br_mount_dir"/lib
cp "$rpi_mount_dir"/lib/arm-linux-gnueabihf/libpthread_nonshared.a "$br_mount_dir"/lib


# Unmount the Raspberry Pi image
echo_info "Unmounting the Raspberry Pi image..."
umount -l "$rpi_mount_dir"
losetup -d "$raspbi_loop"
sudo rmdir "$rpi_mount_dir"


# Unmount the Buildroot OS image
echo_info "Unmounting the Buildroot OS image..."
umount -l "$br_mount_dir"
losetup -d "$br_loop"
sudo rmdir "$br_mount_dir"


echo_info "Status: 'install_g++.sh' script successfully installed g++."
exit 0







