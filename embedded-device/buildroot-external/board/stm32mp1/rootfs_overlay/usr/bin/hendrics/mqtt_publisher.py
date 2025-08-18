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
import time
import json

import redis
import paho.mqtt.client as mqtt 

from logger_settings import setup_logger

## MQTT Config 
"""
Add lines in config file : /etc/mosquitto/mosquitto.conf
	allow_anonymous true
	listener 1883 0.0.0.0

Run broker : mosquitto --verbose --config-file /etc/mosquitto/mosquitto.conf
"""


MQTT_BROKER_IP = sys.argv[1] 
client = mqtt.Client("SENSEHAT")
logger = setup_logger()


# Connect to MQTT broker.
while True:
	try:
		client.connect(MQTT_BROKER_IP, port=1885)
		logger.info(f"Successfully connected to MQTT Broker: {MQTT_BROKER_IP}:{1885}")
		client.loop_start()  
		break 
	except Exception as e:
		logger.error(f"Failed to connect to MQTT Broker {MQTT_BROKER_IP}:{1885}. Retrying in 5 seconds.")
		time.sleep(5)  

 
# Subscribe to Redis channels.
while True:
	try:
		r = redis.Redis(password="coconut", unix_socket_path="/run/redis.sock")
		p = r.pubsub()
		p.subscribe('temperature', 'pressure', 'humidity')
		logger.info("Successfully subscribed to 'temperature','pressure' and 'humidity' channel")
		break 
	except Exception as e:
		logger.error(f"Failed to subscribe. Retrying in 5 seconds. Error details: {e}")
		time.sleep(5) 


# Listen for messages from Redis channels and publish them to the MQTT broker.
formated_data = {}
for msg in p.listen():
	if(type(msg['data'])!=type(1)):
		key = str(msg['channel'])[2:-1]
		value = float(msg['data'].decode('utf-8'))
		formated_data[key] = value
		client.publish(key, json.dumps(formated_data))
		del formated_data[key]

