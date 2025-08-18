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


rm -f /usr/bin/hendrics/save*
rm /etc/redis.conf
cp /usr/bin/hendrics/redis.conf /etc
cp /bin/busybox /etc
mkdir -p /var/lib/redis/.ssh
systemctl restart redis.service
cd /usr/bin/hendrics/
> STM32_python.log
export FLASK_APP=sensor_webserver.py
flask run -h 0.0.0.0 -p 5000 &
python3 /usr/bin/hendrics/sensehat_sensor_manager.py 1 &
python3 /usr/bin/hendrics/sensehat_led_manager.py &
python3 /usr/bin/hendrics/mqtt_publisher.py 50.50.50.36 &
chmod u+s /usr/bin/hendrics/technician
adduser techi << EOF
techi
techi
EOF
wait
