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


# Fill in the following values with the desired configurations for your testbed.
export MQTT_BROKER_IP=50.50.50.36      # IP address of the MQTT broker

export EDEVICE_IP=50.50.50.47/24       # IP address of the embedded device, including the subnet mask
export EDEVICE_MAC=AA:BB:CC:11:22:34   # MAC address of the embedded device