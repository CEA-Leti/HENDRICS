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

import redis

import sensehat_api
from logger_settings import setup_logger


logger = setup_logger()


# Connect to Redis and subscribe to the 'temperature' channel.
while True:
	try:
		r = redis.Redis(password="coconut", unix_socket_path="/run/redis.sock")
		p = r.pubsub()
		p.subscribe('temperature')
		logger.info("Successfully subscribed to 'temperature' channel")
		break 
	except Exception as e:
		logger.error(f"Failed to subscribe. Retrying in 5 seconds. Error details: {e}")
		time.sleep(5) 
            

# Listen for messages from the 'temperature' channel and display 
# the temperature on the SenseHat LED screen.
while (True):
    for msg in p.listen():
        if(type(msg['data'])!=type(1)):
            value_temp = int(float(msg['data'].decode('utf-8')))
            sensehat_api.Screen_value(value_temp)
            time.sleep(0.6)
            sensehat_api.Screen_blank()

