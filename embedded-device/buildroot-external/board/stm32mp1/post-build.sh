#!/bin/sh

set -u
set -e

# Add a console on tty1
if [ -e ${TARGET_DIR}/etc/inittab ]; then
    grep -qE '^tty1::' ${TARGET_DIR}/etc/inittab || \
	sed -i '/GENERIC_SERIAL/a\
tty1::respawn:/sbin/getty -L  tty1 0 vt100 # HDMI console' ${TARGET_DIR}/etc/inittab
fi

# Add an image of the fs for docker containerization

if [ -f " ${TARGET_DIR}/rootfs.tar.gz" ] ; then
        rm " ${TARGET_DIR}/rootfs.tar.gz"
fi

echo "bbbbbbbaaaaaa ${TARGET_DIR}"
tar -cpf ${TARGET_DIR}/../rootfs.tar -C ${TARGET_DIR} --exclude=./proc --exclude=./tmp --exclude=./mnt --exclude=./dev --exclude=./sys .
mv ${TARGET_DIR}/../rootfs.tar ${TARGET_DIR}/rootfs.tar
