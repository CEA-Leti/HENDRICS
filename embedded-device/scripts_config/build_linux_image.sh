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


# This script generates a customized Linux image for our STM32MP1 using Buildroot, 
# including only the essential tools and dependencies required for our testbed.

# Functions to print errors and informational messages
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
RESET="\e[0m"

function echo_info {
    local message="$1"
    echo -e "${GREEN}[+] ${message}${RESET}"
}

function echo_error {
    local message="$1"
    echo -e "${RED}[!] Error: ${message}${RESET}" 1>&2
}

function echo_warning {
    local message="$1"
    echo -e "${YELLOW}${message}${RESET}"
}

function clone_git_repository {
    local repo_name="$1"
    local repo_url="$2"
    local destination_dir="$3"
    local target_branch="$4"

    # Check if the repository has already been cloned; if not, clone it from the provided URL
    if [ -d "$destination_dir/.git" ]; then
        echo_info "$repo_name repository already exists. Skipping cloning."
        git config --global --add safe.directory "$destination_dir"
    else
        echo_info "Cloning the $repo_name repository."
        git clone "$repo_url" "$destination_dir"

        if [ $? -ne 0 ]; then
            echo_error "Failed to clone the $repo_name repository."
            exit 1
        fi
    fi

    # Switch to the specified branch to ensure the desired version is used
    echo_info "Switching to the '$target_branch' branch of the $repo_name repository." 
    cd "$destination_dir"
    git checkout "$target_branch"
    if [ $? -ne 0 ]; then
        echo_error "Failed to switch branches."
        exit 1
    fi
}

# /!\ To ensure the proper execution of this script, the following prerequisites are required:
# Prerequisites for the main script : make, cmake, libtool, autoconf, sudo, wget, fdisk, kmod
# Prerequisites for Buildroot : binutils, diffutils, findutils, build-essential, gcc (version 11.4.0), g++ (version 11.4.0),
# bash, patch, gzip, bzip2, unzip, perl, tar, cpio, rsync, file, bc

# Note: Clang must NOT be installed on the machine, as it can cause issues during Buildroot's compilation,
# especially when compiling systemd-252.4, resulting in missing include file errors.


# Get the directory where the script is located
EDEVICE_DIR="$(realpath "$(dirname "$0")/..")"

# Define the path to the external Buildroot file needed for the compilation
cd "$EDEVICE_DIR"
EXTERNAL="$EDEVICE_DIR/buildroot-external"

# Source the necessary environment variables from the 'network_configuration' file
echo_info "Sourcing the necessary environment variables."
source "$EDEVICE_DIR/network_configuration.sh"
if [ $? -ne 0 ]; then
    echo_error "Unable to source 'network_configuration.sh'."
    exit 1
fi


# Clone Buildroot repository and switch to the '2023.05.x' branch
BUILDROOT_DIR="$EDEVICE_DIR/buildroot"
clone_git_repository "Buildroot" "https://github.com/buildroot/buildroot.git" "$BUILDROOT_DIR" "2023.05.x"


# Clone Socketio repository and switch to the 'v5.3.6' release
mkdir -p embedded-device-app
SOCKETIO_DIR="$EDEVICE_DIR/embedded-device-app/socketio"
clone_git_repository "Socketio" "https://github.com/miguelgrinberg/Flask-SocketIO" "$SOCKETIO_DIR" "v5.3.6"


# Clone Redis repository and switch to the 'v0.4.0' release
REDIS_DIR="$EDEVICE_DIR/embedded-device-app/redis"
clone_git_repository "Redis" "https://github.com/underyx/flask-redis" "$REDIS_DIR" "v0.4.0"


# Configure the Redis shell path in the redis.mk file
echo_info "Executing 'configure_redis_shell.sh' script to configure the Redis shell path."
cd "$EDEVICE_DIR/scripts_config"
./configure_redis_shell.sh "$BUILDROOT_DIR"
if [ $? -ne 0 ]; then
    echo_error "Execution of 'configure_redis_shell.sh' failed."
    exit 1
fi


# Create the defconfig file for the target device
echo_info "Creating the defconfig file for the target device."
cd "$BUILDROOT_DIR"
make BR2_EXTERNAL="$EXTERNAL" edevice_stm32mp1_defconfig
if [ $? -ne 0 ]; then
    echo_error "Failed to create the defconfig file."
    exit 1
fi


# Compile the OS for the target device using Buildroot
echo_info "Starting OS compilation with Buildroot. This may take some time (up to an hour or more depending on hardware)."
sleep 4
make 
if [ $? -eq 0 ]; then
    echo_info "Compilation completed successfully.\n"
else 
    echo_error "Compilation failed."
    exit 1
fi


echo_warning "We have successfully created the STM32 image using Buildroot."
echo_warning "However, to complete the setup, we need to configure and install a few additional components on the image."
echo_warning "To do so, we need to mount the image, which requires sudo privileges."
sudo -v
echo ""

# Check if the required environment variables are set
echo_info "Checking if required environment variables are set."
required_vars=("MQTT_BROKER_IP" "EDEVICE_IP" "EDEVICE_MAC")
for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo_error "'$var' environment variable is not set in the 'network_configuration.sh' file. Please define it."
        exit 1
    fi
done


# Update the MQTT broker IP address and the frequency of data publishing of the SenseHat in seconds
# Note: These parameters are updated after the image is compiled, allowing for configuration changes 
# without the need to rebuild the entire image.
echo_info "Running 'configure_mqtt_publisher.sh' script to configure MQTT broker IP address and the frequency of data publishing of the SenseHat in seconds."
FREQUENCY=2 # Frequency (in seconds) for data retrieval
cd "$EDEVICE_DIR/scripts_config"
sudo ./configure_mqtt_publisher.sh "$BUILDROOT_DIR/output/images/sdcard.img" "${MQTT_BROKER_IP}" "${FREQUENCY}"
if [ $? -ne 0 ]; then
    echo_error "Execution of 'configure_mqtt_publisher.sh' failed."
    exit 1
fi

# Update the STM32 IP and MAC address
echo_info "Running 'configure_network_address.sh' script to configure STM32 IP and MAC address."
sudo ./configure_network_address.sh "$BUILDROOT_DIR/output/images/sdcard.img" "${EDEVICE_IP}" "${EDEVICE_MAC}"
if [ $? -ne 0 ]; then
    echo_error "Execution of 'configure_network_address.sh' failed."
    exit 1
fi


# Download Raspberry Pi image file
echo_info "Downloading Raspberry Pi image file."
cd "$EDEVICE_DIR/scripts_config"
rm -f ./2023-10-10-raspios-bookworm-armhf.img.xz
wget https://downloads.raspberrypi.com/raspios_armhf/images/raspios_armhf-2023-10-10/2023-10-10-raspios-bookworm-armhf.img.xz
if [ $? -ne 0 ]; then
    echo_error "Failed to download Raspberry Pi image file."
    exit 1
fi


# Unzip the downloaded .img file
echo_info "Unzipping the .img file."
xz -d -f ./2023-10-10-raspios-bookworm-armhf.img.xz
if [ $? -ne 0 ]; then
    echo_error "Failed to unzip the .img file."
    exit 1
fi


# Install the g++ compiler in the STM32 .img file.
# Note: Buildroot doesn't support direct installation of compilers on the target system.
# Therefore, we add g++ after the image compilation, as g++ is required by OpenPLC to compile the automation logic.
# To achieve this, we extract a precompiled version of g++ from a Raspberry Pi image that is compatible with our build.
echo_info "Running 'install_g++.sh' script to install g++ in the STM32 .img file."
cd "$EDEVICE_DIR/scripts_config"
sudo ./install_g++.sh "$BUILDROOT_DIR/output/images/sdcard.img" "$EDEVICE_DIR/scripts_config/2023-10-10-raspios-bookworm-armhf.img"
if [ $? -ne 0 ]; then
    echo_error "Execution of 'install_g++.sh' failed."
    exit 1
fi


# Clone the OpenPLC_v3 repository
cd "$EDEVICE_DIR"
OPENPLC_DIR="./OpenPLC_v3"  
if [ -d "$OPENPLC_DIR/.git" ]; then
    echo_info "OpenPLC_v3 repository already exists. Skipping cloning."
else
    echo_info "Cloning the OpenPLC_v3 repository from GitHub."
    git clone https://github.com/thiagoralves/OpenPLC_v3.git
    if [ $? -ne 0 ]; then
        echo_error "Failed to clone the OpenPLC_v3 repository."
        exit 1
    fi
fi


# Checking out to a specific commit in the OpenPLC_v3 repository to ensure compatibility with the current project
# Note : This avoids potential issues with future updates to OpenPLC that could introduce bugs.
echo_info "Checking out commit 2c01258b0f83b459c10514d36bd3e872a349a064 in the OpenPLC_v3 repository."
cd "$EDEVICE_DIR/OpenPLC_v3"
git checkout 2c01258b0f83b459c10514d36bd3e872a349a064
if [ $? -ne 0 ]; then
    echo_error "Failed to checkout the specified commit."
    exit 1
fi


# Install OpenPLC_v3 in the STM32 .img file
echo_info "Running 'install_OpenPLC.sh' script to install OpenPLC_v3 in the .img file."
cd "$EDEVICE_DIR/scripts_config"
sudo ./install_OpenPLC.sh "$BUILDROOT_DIR/output/images/sdcard.img" "$BUILDROOT_DIR/output/host/bin" "$EDEVICE_DIR/OpenPLC_v3" "$EDEVICE_DIR/scripts_config/toolchain.cmake"
if [ $? -ne 0 ]; then
    echo_error "Execution of 'install_OpenPLC.sh' failed."
    exit 1
fi


# Final message indicating setup completion
echo_info "Setup of the .img file for the STM32 is complete. You can now flash the image onto the STM32 SD card."
exit 0
