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

# The name of the target operating system
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Which compilers to use for C and C++
set(CMAKE_C_COMPILER /home/eEDR_testbed/embedded-device/buildroot/output/host/bin/arm-buildroot-linux-gnueabihf-gcc)
set(CMAKE_CXX_COMPILER /home/eEDR_testbed/embedded-device/buildroot/output/host/bin/arm-buildroot-linux-gnueabihf-g++)

# Where is the target environment located
set(CMAKE_FIND_ROOT_PATH /home/eEDR_testbed/embedded-device/scripts_config/../buildroot/output/host/arm-buildroot-linux-gnueabihf/sysroot)

# Search programs in the host environment
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# Search headers and libraries in the target environment
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
