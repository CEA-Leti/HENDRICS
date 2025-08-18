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

import subprocess
import datetime
import time
import shutil
import os
import socket
import random
import re
from concurrent.futures import ThreadPoolExecutor

import redis
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_redis import FlaskRedis

from logger_settings import setup_logger

logger = setup_logger()

executor = ThreadPoolExecutor(1)

template_dir='/var/www/sensor_webserver/templates'
static_dir='/var/www/sensor_webserver/static'
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['REDIS_URL'] = "unix:///run/redis.sock?password=coconut"


# Connect to Redis and subscribe to the channels.
while True:
	try :
		redis_client = FlaskRedis(app)
		p = redis_client.pubsub()
		p.subscribe('temperature', 'pressure', 'humidity')
		logger.info("Successfully subscribed to 'temperature','pressure' and 'humidity' channel")
		break
	except Exception as e:
		logger.error(f"Failed to subscribe. Retrying in 5 seconds. Error details: {e}")
		time.sleep(5) 

# Listen for incoming Redis messages and emit them via SocketIO to connected clients.
def read_redis_message():
	for msg in p.listen():
		data=str(msg['channel'])[2:-1]+" "+str(msg['data'])[2:-1]
		socketio.emit('SENSE_DATA', {'message': data + " " + str(datetime.datetime.now())}, namespace='/')

executor.submit(read_redis_message)


# ---------------------- Flask Routes ----------------------

# Main dashboard displaying live sensor data.
@app.route("/", methods=['GET', 'POST'])
def hello_world():
	return render_template('index.html')

# Page providing a graphical interface for sending queries to the Redis database.
@app.route("/nosql", methods=['GET'])
def nosql():
	return render_template('nosql.html')

# Send queries to the Redis database using a Lua script (used in the “Redis Lua injection” attack).
@app.route('/process', methods=['POST'])
def process():
	"""Handle data processing requests on Redis database using a Lua script."""

	data = request.form['dataSelect']
	lua_script = """local hashValues = redis.call('HVALS', '{key}')
		local numValues = #hashValues
		local numLines = 10

		-- If the number of values is lower or equal to 10, then return all the values
		if numValues <= numLines then
			return hashValues
		else
			-- If the number of values is more than 10, then retrieve the 10 last values
			local lastTenValues = {{}}
			for i = numValues - numLines + 1, numValues do
				table.insert(lastTenValues, hashValues[i])
			end
			return lastTenValues
		end""".format(key = data)
	
	try:
		registered_script = redis_client.register_script(lua_script)
		logger.info("Lua script has been executed successfully.")
		resultats = registered_script()
		return str(resultats)
	
	except redis.exceptions.ResponseError as e:
		logger.error(f"Error while executing the Lua script on the Redis client: {e}")
		return str("Error while executing the Lua script:"+ str(e))


# Page providing a graphical interface for triggering the Redis backup script.
@app.route('/backup', methods=['GET'])
def backup():
	return render_template('backup.html')

# Triggers Redis backup script (used in the "ICMP exfiltration" attack).
@app.route('/performBackup', methods=['POST'])
def Dobackup():
	try:
		os.system("/bin/bash /etc/backup.sh")
		return "/etc/backup.sh : Backup done."
	except :
		logger.error("An error occurred while trying to perform backup")
		return "/etc/backup.sh : An error occurred while trying to perform backup."


# Used to restore the target system after the “Mirai Malware” attack, by rebooting.
@app.route('/reboot', methods=['GET'])
def remote_reboot():
    root_password = "root"
    cmd = f"echo '{root_password}' | su -c 'reboot'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return "Reboot command issued successfully.", 200
    else:
        return f"Failed to issue reboot: {result.stderr}", 500


# Used to restore the BusyBox binary after the "BusyBox Deletion Attack".
@app.route('/busybox', methods=['GET'])
def busybox():
	shutil.copy("/etc/busybox", "/bin/busybox")
	return "Busybox is back." 
