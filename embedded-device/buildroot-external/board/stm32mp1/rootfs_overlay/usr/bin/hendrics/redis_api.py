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

import redis

from logger_settings import setup_logger 

logger = setup_logger()


def store_data(redis_client, hash_name, timestamp, sensor_value):
    try:
        # Store the sensor value in the Redis DataBase using the timestamp as the field key.
        redis_client.hset(hash_name, key=timestamp, value=sensor_value)
        logger.info(f"Data stored successfully: Hash_name='{hash_name}', Timestamp='{timestamp}', Value='{sensor_value}'")
    except Exception as e:
        logger.error(f"Unable to store data in Redis DataBase: {e}")


def retrieve_data(redis_client, timestamp):
    try:
        # Use of the HGETALL methode to obtain all the fields and their associated value.
        data = redis_client.hgetall("mesures")
        logger.info(f"Data retrieved successfully from Redis DataBase")
    except Exception as e:
        logger.error(f"Unable to retrieve data from Redis DataBase: {e}")

    if timestamp in data:
        return data[timestamp]
    else:
        return None

