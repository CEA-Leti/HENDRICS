#! /bin/bash 
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


if [ $# -ne 2 ]; then
    echo "[!] Error: 'restauration.sh' script expects exactly 2 argument, but received $#."
    echo "[!] Usage: $0 <Target IP Address> <Attack Mode>"
    echo "[!] Note: The attack mode must match the one used during the attack."
    exit 1
fi

ROOT_USERNAME=root
ROOT_PASSWORD=root
REDIS_PASSWORD=coconut
SENSOR_WEBSERVER_PORT=5000

target_ip_address=$1
attack_mode=$2

if ! (ping -c 1 -W 2 $target_ip_address > /dev/null 2>&1); then
	echo "[!] Error: Invalid IP address or host unreachable."
    exit 1
fi

case $attack_mode in
    (s|S)
        echo "[+] Removing the public SSH key added during the attack."
        echo "[+] Deleting the SSH key entry from the Redis server database."
        redis-cli -h $target_ip_address -a $REDIS_PASSWORD del ssh_key
        echo "[+] Restoring the default Redis save file name (dump.rdb)."
        redis-cli -h $target_ip_address -a $REDIS_PASSWORD config set dbfilename dump.rdb
        echo "[+] Restoring the default Redis home directory (/var/lib/redis)."
        redis-cli -h $target_ip_address -a $REDIS_PASSWORD config set dir /var/lib/redis
        sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR $ROOT_USERNAME@$target_ip_address <<EOF
            rm -f /var/lib/redis/.ssh/authorized_keys
EOF
        ;;

    (b|B)
        echo "[+] Restoring the default Redis save file name (dump.rdb)."
        redis-cli -h $target_ip_address -a $REDIS_PASSWORD config set dbfilename dump.rdb
        echo "[+] Restoring the default Redis home directory (/var/lib/redis)."
        redis-cli -h $target_ip_address -a $REDIS_PASSWORD config set dir /var/lib/redis
        echo "[+] Restoring BusyBox on the target machine."
        curl http://$target_ip_address:$SENSOR_WEBSERVER_PORT/busybox
        echo ""
        ;;

    (l|L)
        echo "[+] Restarting the Redis service on the target machine."
        sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR $ROOT_USERNAME@$target_ip_address <<EOF
            systemctl restart sensehat.service
EOF
        ;;

    (*)
        echo -e "[!] Invalid option.\n"
        exit 1
        ;;
esac

sleep 10  # Pause to ensure the Sense HAT services has enough time to fully restart
echo "[+] Restoration process complete."

