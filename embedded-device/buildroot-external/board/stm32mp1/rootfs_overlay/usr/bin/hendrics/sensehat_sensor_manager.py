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

import time
import sys

import redis

import sensehat_api
from redis_api import *
from logger_settings import setup_logger 

logger = setup_logger()

# Create redis_client via unix socket.
while True:
	try:
		redis_client = redis.Redis(password="coconut", unix_socket_path="/run/redis.sock")
		redis_client.ping()
		logger.info("Successfully connected to Redis")
		break
	except Exception as e:
		logger.error(f"Failed to connect to Redis. Retrying in 5 seconds. Error details: {e}")
		time.sleep(5) 


data_temp = {
	"temperature": 0
}
data_hum = {
	"humidity": 0
}
data_press = {
	"pressure": 0
}

sensehat_api.init()


while True:
	# Get Sensehat datas via I2C bus.
	data_temp["temperature"] = sensehat_api.get_temperature_from_pressure()
	data_hum["humidity"] = sensehat_api.get_humidity()
	data_press["pressure"] = sensehat_api.get_pressure()

	timestamp = str(int(time.time()))

 	# Publishing datas into Redis server.
	try:
		redis_client.publish('temperature', data_temp["temperature"])
		redis_client.publish('pressure', data_press["pressure"])
		redis_client.publish('humidity', data_hum["humidity"])
	except Exception as e:
		logger.error(f"Failed to publish on Redis server: {e}")
	
	# Storing datas into Redis DataBase.
	store_data(redis_client, "Temperature", timestamp, data_temp["temperature"])
	store_data(redis_client, "Humidity", timestamp, data_hum["humidity"])
	store_data(redis_client, "Pressure", timestamp, data_press["pressure"])

	time.sleep(int(sys.argv[1]))


