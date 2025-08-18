#!/usr/bin/python3
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

import socket
from time import sleep
import sys

transaction_identifier = b"\x18\x03"	
protocol_identifier = b"\x00\x00"	
lenght_field = b"\x00\x06"		
mod_function = b"\x05"

exception_code = b'\x85'


def decimal_to_hex_bytes(value):
	if not (0 <= value <= 65535):
		print("Invalid coil value: it must be a number between 0 and 65535.")
		sys.exit(1)
	
	return value.to_bytes(2, byteorder='little')

def exception(code):
	return {
		b"\x01" : "ILLEGAL FUNCTION",
		b"\x02" : "ILLEGAL DATA ADDRESS",
		b"\x03" : "ILLEGAL DATA VALUE",
		b"\x04" : "ILLEGAL RESPONSE LENGTH",
		b"\x05" : "ACKNOWLEDGE",
		b"\x06" : "SLAVE DEVICE BUSY",
		b"\x07" : "NEGATIVE ACKNOWLEDGE",
		b"\x08" : "MEMORY PARITY ERROR"
	}.get(code, "Wrong exception code... Probably the host is not running ModBus...")

def main():
	
	address= sys.argv[1]
	port= sys.argv[2]
	slave_id= sys.argv[3]
	register= sys.argv[4]
	value= sys.argv[5]
	
	slave_address = bytes([int(slave_id)])
	register = int(register).to_bytes(2,'big')
	
	try:
		value_byte = decimal_to_hex_bytes(int(value))
		complete_data = register + value_byte
			
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		s.settimeout(3)

		s.connect((address,int(port)))
		payload = transaction_identifier + protocol_identifier +lenght_field + slave_address + mod_function + complete_data
		s.send(payload)
		response = s.recv(256)
		s.close()
		
		if (response[0:5] == b"\x18\x03\x00\x00\x00") and (response[7:8] == mod_function) :
			print("\n[+] WRITTEN VALUE: ", int.from_bytes(response[-2:],'little'))
		elif (response[0:5] == b"\x18\x03\x00\x00\x00") and (response[7:8] == exception_code) :
			print("[!] Exception thrown:")
			print(exception(response[8:9]))
		else:
			print("[!] Operation failed... Error getting ModBus response...")
	except:
		print("[!] Host is offline or you specified a wrong port...")
	
		
if __name__ == "__main__" :
	main()
