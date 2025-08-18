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


# Check if the number of arguments passed to the script is exactly one
if [ $# -ne 1 ]; then
    echo_error "'configure_redis_shell.sh' script expects exactly 1 argument, but received $#."
    echo "[!] Usage: sudo $0 <path/to/buildroot>"
    exit 1
fi


# Modify the redis.mk file to configure Redis shell path
path="$1" 
if [ -f "$path/package/redis/redis.mk" ]; then 
    sed -i 's|/bin/false|/bin/sh|g' "$path/package/redis/redis.mk"
    if [ $? -eq 0 ]; then
        echo_info "Status: 'configure_redis_shell.sh' script successfully modified 'redis.mk'."
        exit 0
    else :
        echo_error "Failed to modify the 'redis.mk' file."
        exit 1
    fi
else 
    echo_error "The 'redis.mk' file cannot be found at '$path/package/redis/redis.mk'."
    exit 1
fi 



