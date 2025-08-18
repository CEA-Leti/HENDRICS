# Data Exfiltration Via ICMP

## Attack Overview
In this scenario, you are an attacker who has gained access to a Redis server. The goal of this attack is to exfiltrate a file from the target system using ICMP packets.

The target Redis server has a backup mechanism set up, which is normally used to create backups of the Redis database. We are going to exploit this mechanism by overwriting the backup script with a malicious Bash script designed to read a specific file on the target system and encode its contents into ICMP packets. As a result, when the backup process is triggered, the malicious script is executed and data is exfiltrated.

To carry out the attack, we proceed as follows:
1. **Run a Rogue Redis Server:** First, on the attacker's machine, we start a rogue Redis server. This server connects to the target Redis server and modifies its configuration to make it a slave of the rogue server. As a result, the target Redis server's database is synchronized with the rogue Redis server’s database.
2. **Overwrite the Backup Script:** We're going to take advantage of the synchronization process to overwrite the backup script on the target system. To do this, before initiating synchronization, the rogue Redis server reconfigures the working directory of the target Redis server to point to the directory containing the backup script. Additionally, the rogue Redis server reconfigures the target Redis server to treat the backup script as its database file. Once this is done, we initiate the synchronization, and the backup script is overwritten with the malicious script sent by the rogue server.
3. **Set Up ICMP Listener:** Once the malicious Bash script is uploaded, we stop the rogue Redis server. On the attacker’s machine, we now start a Python script to listen and capture the ICMP packets sent by the target Redis server. This script decodes the ICMP packets and reconstructs the contents of the exfiltrated file.
4. **Trigger the Backup Mechanism:** To execute the malicious script, we exploit the Sensor web server running on the target system. This server exposes an endpoint `/performBackup`, which is used to trigger Redis backups. By sending a POST request to this endpoint, we initiate the backup process. This action causes the Redis server to execute the malicious script, triggering the exfiltration of data via ICMP packets to the attacker’s listener.

The rogue Redis server used in this attack is sourced from the [redis-rogue-server](https://github.com/n0b0dyCN/redis-rogue-server) project on GitHub.

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

You also need to install Curl and Python. You can install them with the following command:   
```bash
sudo apt install curl python3 python3-pip
```

Additionally, you’ll need the 'scapy' Python library. You can install it by running:  
```bash
pip install scapy==2.6.1
```

## Attack Execution
To execute the attack, run the following command:  
```bash
sudo ./exploit.sh 
```

Alternatively, you can run the attack in non-interactive mode using:  
```bash
sudo ./exploit.sh -all <Target IP Address> <Redis Password> <Path to the file to exfiltrate>
```

## System Restoration
To restore the system to its state prior to the attack, execute the following command:  
```bash
./restoration.sh <Target IP Address>
```

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in this attack:  

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0845        | Program Upload           |The goal of this attack is to retrieves a file from the target system.    | 
| T0848        | Rogue Master             |The target Redis server is configured as a slave to a rogue Redis server. |
| T0853        | Scripting                |The exfiltration is performed using a custom Bash script.                 | 
| T0859        | Valid Accounts           |Valid Redis credentials are used to access and reconfigure the server.    |  

> [!NOTE]
> This table is based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
