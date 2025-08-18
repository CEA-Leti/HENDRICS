# Redis Lua injection attack

## Attack Overview
In this scenario, you are an attacker who has discovered a Sensor Web server running on a target device. The goal of this attack is to exploit this web server to enable the execution of arbitrary commands on the Redis server.

The Sensor Web server is responsible for displaying various information from the sensor. To achieve this, it communicates with the Redis server to get the sensor data. Among the available endpoints on the web server, there is one called `/process`, which is used to retrieve data associated with a specific key, such as "temperature" data. However, this endpoint is vulnerable to injection attacks.

By injecting a Lua script into a request to the `/process` endpoint, we can trick the Redis server into executing the Lua script. This allows us to execute command on the Redis server.

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

You also need to install Python. You can install it with the following command:  
```bash
sudo apt install python3 python3-pip
```

Additionally, you’ll need the 'requests' Python library. You can install it by running: 
```bash
pip install requests==2.25.1
```

## Attack Execution
To execute the attack, run the following command:  
```bash
./exploit.sh 
```

If you prefer, to execute the attack in non-interactive mode, specify the target's IP address and the Redis command :  
```bash
./exploit.sh -all -c <Target IP Address> <Redis Command>
```

Alternatively, you can specify a Lua script instead of a Redis command: 
```bash
./exploit.sh -all -s <Target IP Address> <Lua Script>
```

The specified Lua script must be located in the `lua_scripts/` directory.

## System Restoration
To restore the system to its state prior to the attack, execute the following command:  
```bash
./restoration.sh <Target IP Address>
```

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in this attack:  

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0853        | Scripting                |The attack uses Lua scripts to achieve command execution on the Redis server.          | 
| T0866        | Exploitation of Remote Services |A vulnerable web endpoint is exploited to execute commands on the Redis server. |
| T0871        | Execution through API    |The attacke script communicates with the Sensor Web server via its REST API.           |

> [!NOTE]
> This table is based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
