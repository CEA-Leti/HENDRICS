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


EXFILTRATION_DNS_DIR="$(realpath "$(dirname "$0")/..")"

dnsteal_repo_url="https://github.com/m57/dnsteal.git"
dnsteal_src_dir="$EXFILTRATION_DNS_DIR/dnsteal"
target_commit_hash="1b09d21585904ce111755cd8d0fc41ee662fc2e4"

patch_file="$EXFILTRATION_DNS_DIR/scripts/patch_dnsteal_hendrics.patch"
patch_commit_name="Patch DNSteal Hendrics"


# Check if the DNSteal repository has already been cloned. If not, clone it from the repository URL
if [ -d "$dnsteal_src_dir/.git" ]; then
    echo "[+] DNSteal repository already exists. Skipping cloning."
    git config --global --add safe.directory "$dnsteal_src_dir"
else
    echo "[+] Cloning the DNSteal repository from $dnsteal_repo_url."
    git clone "$dnsteal_repo_url" "$dnsteal_src_dir" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "[!] Failed to clone the DNSteal repository."
        exit 1
    fi
fi

cd "$dnsteal_src_dir"

# Check if the repository is already at the desired commit and has the patch applied.
if ! (git log | grep -q "$patch_commit_name"); then

    # Checkout the specified commit to ensure we use a stable version
    echo "[+] Checking out the commit '$target_commit_hash'."
    git checkout "$target_commit_hash" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "[!] Failed to checkout the commit."
        exit 1
    fi

    # Apply the patch to the repository
    echo "[+] Applying the patch."
    export GIT_COMMITTER_NAME="CEA"
    export GIT_COMMITTER_EMAIL="https://www.cea.fr/"
    git am --whitespace=nowarn < "$patch_file"
    if [ $? -ne 0 ]; then
        echo "[!] Failed to apply the patch."
        exit 1
    fi
fi
