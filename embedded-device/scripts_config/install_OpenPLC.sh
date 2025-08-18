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


# Function to compile OpenPLC sources
compiling_openplc_sources() {
    echo_info "Starting the compilation of OpenPLC sources..."

    # Check if the provided directories exist
    if [ ! -d "$1" ]; then
        echo_error "Directory ${1} does not exist."
        exit 1
    elif [ ! -d "$2" ]; then
        echo_error "Directory ${2} does not exist."
        exit 1
    fi

    cross_gcc=""
    cross_gxx=""

    # Locate the cross compiler for gcc
    while IFS= read -r file; do
        if [ -z "$cross_gcc" ]; then
            echo_info "Found gcc command: $file"
            cross_gcc="$file"
        fi
    done < <(find "$1" -name "*buildroot-*-gcc" 2>/dev/null)

    # Locate the cross compiler for g++
    while IFS= read -r file2; do
        if [ -z "$cross_gxx" ]; then
            echo_info "Found g++ command: $file2"
            cross_gxx="$file2"
        fi

    done < <(find "$1" -name "*buildroot-*-g++" 2>/dev/null)

    # Update toolchain configuration file
    echo_info "Updating toolchain.cmake file..."
    sed -i "s|set(CMAKE_C_COMPILER .*)|set(CMAKE_C_COMPILER $cross_gcc)|" "$3"
    sed -i "s|set(CMAKE_CXX_COMPILER .*)|set(CMAKE_CXX_COMPILER $cross_gxx)|" "$3"
    sed -i "s|set(CMAKE_FIND_ROOT_PATH .*)|set(CMAKE_FIND_ROOT_PATH $SCRIPTDIR/../buildroot/output/host/arm-buildroot-linux-gnueabihf/sysroot)|" "$3"


    # Check if the required libraries are installed
    export PATH="$PATH":$1
    echo_info "Checking if required libraries are installed."
    libraries=("libtool" "autoconf" "cmake" "make")
    for lib in "${libraries[@]}"; do
        if (dpkg -s "$lib" > /dev/null 2>&1); then
            echo_info "$lib is installed."
        else
            echo_error "$lib is not installed."
            echo "[!] The 'install_OpenPLC.sh' script requires the following libraries: libtool, autoconf, cmake, and make."
            exit 1
        fi
    done


    # Prepare results directory for the compilation output
    cd "$2"
    mkdir -p results
    cd results
    mkdir -p matiec st_optimizer glue_generator usr-local-include usr-local-lib
    cd ..


    # Compile matiec sources
    echo_info "Compiling matiec sources..."
    cd utils/matiec_src
    autoreconf -i
    ./configure --host=arm-buildroot-linux-gnueabihf --build=x86_64-linux-gnu
    make CXX="$cross_gxx" CC="$cross_gcc" || { echo_error "Compilation failed for matiec."; exit 1;}

    cp iec2c iec2iec ../../results/matiec
    cp iec2c iec2iec ../../webserver

    # Compile st_optimizer sources
    echo_info "Compiling st_optimizer source..."
    cd ../st_optimizer_src
    "$cross_gxx" st_optimizer.cpp -o st_optimizer || { echo_error "Compilation failed for st_optimizer."; exit 1; }

    cp st_optimizer ../../results/st_optimizer
    cp st_optimizer ../../webserver

    # Compile the glue generator sources
    echo_info "Compiling the glue generator source..."
    cd ../glue_generator_src
    "$cross_gxx" -std=c++11 glue_generator.cpp -o glue_generator || { echo_error "Compilation failed for glue generator."; exit 1; }

    cp glue_generator ../../results/glue_generator
    cp glue_generator ../../webserver/core

    # Compile OpenDNP3 libraries
    echo_info "Compiling OpenDNP3 libraries..."
    cd ../dnp3_src
    cmake -DCMAKE_TOOLCHAIN_FILE="$3" .
    make CXX="$cross_gxx" CC="$cross_gcc" || { echo_error "Compilation failed for OpenDNP3."; exit 1; }
    make CXX="$cross_gxx" CC="$cross_gcc" install || { echo_error "Installation failed for OpenDNP3."; exit 1; }

    cp -r /usr/local/include/asio* /usr/local/include/open* /usr/local/include/dnp3decode ../../results/usr-local-include

    cp /usr/local/lib/libasio* /usr/local/lib/libopen* ../../results/usr-local-lib

    # Compile Modbus libraries
    echo_info "Compiling Modbus libraries..."
    cd ../libmodbus_src
    ./autogen.sh
    ./configure --host=arm-buildroot-linux-gnueabihf --build=x86_64-linux-gnu
    make CXX="$cross_gxx" CC="$cross_gcc" install || { echo_error "Compilation failed for Modbus."; exit 1; }

    cp -r /usr/local/include/modbus ../../results/usr-local-include
    cp -r /usr/local/lib/libmodbus* /usr/local/lib/pkgconfig ../../results/usr-local-lib
    
    echo_info "OpenPLC Compilation process completed successfully..."
}


# Function to install compiled files
installing_files(){
    echo_info "Starting installation of the compiled OpenPLC files..."


    # Mount the 4th partition of the image file
    br_mount_dir="/mnt/eEDR_testbed/br"
    mkdir -p "$br_mount_dir"
    echo_info "Mounting the OS buildroot image filesystem..."
    br_loop=$(losetup -f --show -P "$img_file")
    sudo mount -o loop "$br_loop"p4 "$br_mount_dir"
    if [ $? -ne 0 ]; then
        echo_error "Unable to mount the filesystem of the sdcard.img file."
        losetup -d "$br_loop"
        exit 1
    fi


    # Copy shared object files to the mounted file system
    echo_info "Retrieving necessary shared object files from compilation..."
    cp "$OpenPLC_dir"/results/usr-local-lib/libmodbus.so.5.1.0 "$br_mount_dir"/usr/lib
    cp "$OpenPLC_dir"/results/usr-local-lib/libopendnp3.so "$br_mount_dir"/usr/lib
    cp "$OpenPLC_dir"/results/usr-local-lib/libopenpal.so "$br_mount_dir"/usr/lib
    cp "$OpenPLC_dir"/results/usr-local-lib/libasiopal.so "$br_mount_dir"/usr/lib
    cp "$OpenPLC_dir"/results/usr-local-lib/libasiodnp3.so "$br_mount_dir"/usr/lib
    

    # Create symbolic links for the shared object files
    cd "$br_mount_dir"/usr/lib 
    ln -s libmodbus.so.5.1.0 libmodbus.so
    ln -s libmodbus.so.5.1.0 libmodbus.so.5
    cd "$SCRIPTDIR"


    # Copy header files to the mounted file system
    echo_info "Retrieving header files from compilation..."
    cd "$br_mount_dir"/usr
    cp -r "$OpenPLC_dir"/results/usr-local-include/asiodnp3 ./include 
    cp -r "$OpenPLC_dir"/results/usr-local-include/asiopal ./include 
    cp -r "$OpenPLC_dir"/results/usr-local-include/dnp3decode ./include 
    cp -r "$OpenPLC_dir"/results/usr-local-include/modbus ./include 
    cp -r "$OpenPLC_dir"/results/usr-local-include/opendnp3 ./include
    cp -r "$OpenPLC_dir"/results/usr-local-include/openpal ./include 
    cd "$SCRIPTDIR"


    # Create configuration scripts
    echo_info "Creating configuration scripts..."
    cat << EOF > "$OpenPLC_dir/start_openplc.sh"
#!/bin/bash
mkdir -p /persistent/st_files
cp -n /workdir/webserver/dnp3_default.cfg /persistent/dnp3.cfg
cp -n /workdir/webserver/openplc_default.db /persistent/openplc.db
cp -n /workdir/webserver/st_files_default/* /persistent/st_files/
cp -n /dev/null /persistent/persistent.file
cp -n /dev/null /persistent/mbconfig.cfg
cd /etc/OpenPLC_v3/webserver
/etc/.venv/bin/python3 webserver.py
EOF

    # Make the configuration script executable
    chmod +x "$OpenPLC_dir/start_openplc.sh"

    # Create the systemd service file for OpenPLC
    output_file="$br_mount_dir/etc/systemd/system/openplc.service"
    cat << EOF > "$output_file"
[Unit]
Description=OpenPLC Service
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
Group=root
WorkingDirectory=/etc/OpenPLC_v3
ExecStart=/etc/OpenPLC_v3/start_openplc.sh

[Install]
WantedBy=multi-user.target
EOF

    # Make the systemd service file executable
    chmod +x $output_file

    # Copy the compile program script
    cp compile_program.sh "$OpenPLC_dir/webserver/scripts/"
    chmod +x "$OpenPLC_dir/webserver/scripts/compile_program.sh"
    cp -r "$OpenPLC_dir" "$br_mount_dir/etc"
    sleep 5

    # Unmount the OS buildroot image
    umount -l "$br_mount_dir"
    if [ $? -ne 0 ]; then
        echo_error "Unable to unmount the filesystem of the sdcard.img file."
        exit 1
    fi

    losetup -d "$br_loop"
    sudo rmdir "$br_mount_dir"

    echo_info "Installation of compiled files completed successfully..."
}


# Check if the number of arguments passed to the script is exactly four
if [ $# -ne 4 ]; then
    echo_error "'install_OpenPLC.sh' script expects exactly 4 argument, but received $#."
    echo "[!] Usage: sudo $0 </path/to/buildroot/output/images/sdcard.img> </path/to/buildroot/output/host/bin> </path/to/OpenPLC_git> </path/to/toolchain.cmake>"
    exit 1
fi


# Check if the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo_error "Script '$0' must be run as root."
   exit 1
fi


# Variable declarations
SCRIPTDIR="$(realpath "$(dirname "$0")")"
img_file="$1"
toolchain_dir="$2"
OpenPLC_dir="$3"
cmake_toolchain="$4"


# Compile OpenPLC sources
compiling_openplc_sources "$toolchain_dir" "$OpenPLC_dir" "$cmake_toolchain"


# Install OpenPLC compiled files
installing_files "$1"

echo_info "Status: 'install_OpenPLC.sh' script successfully installed OpenPLC."
exit 0