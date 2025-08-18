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


packet_count=0
payload_length=$1

input_file="/tmp/pkt$payload_length"
temp_file="/tmp/tmp-pkt"
output_file="/tmp/payloads$payload_length"

rm -f "$output_file"
touch "$output_file"

while [ -s "$input_file" ]
do
	packet_length=$(($payload_length+9))

	/bin/head -c $packet_length "$input_file" > "$temp_file"

	/bin/tail -c $payload_length "$temp_file" >> "$output_file"

	/bin/tail -c +$(($packet_length + 1)) "$input_file" > "$temp_file"

	/bin/cat "$temp_file" > "$input_file"

	packet_count=$(($packet_count + 1))

done

echo $packet_count

/bin/rm -f "$input_file"

