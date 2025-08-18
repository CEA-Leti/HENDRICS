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


BOOPKIT_DIR="$(realpath "$(dirname "$0")/..")"
compile_boopkit_boop=$1

boopkit_repo_url="https://github.com/krisnova/boopkit.git"
boopkit_src_dir="$BOOPKIT_DIR/boopkit_src"
target_commit_hash="b8dc4ee0c9a7eeb042e20835f26591776f7a6cff"

patch_file="$BOOPKIT_DIR/scripts/patch_boopkit_hendrics.patch"
patch_commit_name="Patch Boopkit Hendrics"


# Check if the Boopkit repository has already been cloned. If not, clone it from the repository URL
if [ -d "$boopkit_src_dir/.git" ]; then
    echo "[+] Boopkit repository already exists. Skipping cloning."
    git config --global --add safe.directory "$boopkit_src_dir"
else
    echo "[+] Cloning the Boopkit repository from $boopkit_repo_url."
    git clone "$boopkit_repo_url" "$boopkit_src_dir" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "[!] Failed to clone the Boopkit repository."
        exit 1
    fi
fi

cd "$boopkit_src_dir"

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

cd "boop"

# Compile the 'boopkit-boop.c' if the user has requested it and it doesn't already exist
if [ ! -f "boopkit-boop" ]; then
    if [ "$compile_boopkit_boop" -eq 1 ]; then
        echo "[+] Compiling 'boopkit-boop.c', the program used to trigger Boopkit."
        make
        if [ $? -eq 0 ]; then
            echo "[+] Successfully compiled 'boopkit-boop.c'."
        else
            echo "[!] Compilation of 'boopkit-boop.c' failed."
            exit 1
        fi
    fi
fi