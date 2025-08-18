# Redis Global Attack

## Attack Overview
In this scenario, you are an attacker who has discovered a Redis server on a target device protected by a weak password. The goal of this attack is to first gain access to the Redis server, and then leverage that access to perform malicious actions on the target system.

To gain access, we begin by performing a dictionary attack using `hydra`, which allows us to successfully brute-force the Redis password. Once authenticated, we can perform one of several attacks depending on the objective:  
1. **SSH Key Injection Attack:** By abusing Redis's ability to write to the file system, we inject our own SSH public key into the authorized keys file of the `redis` user. This grants us direct SSH access to the target system as the redis user.  
2. **BusyBox Deletion Attack:** In this attack, we overwrite the BusyBox binary with a simple text file. BusyBox provides essential Linux command implementations in embedded systems, so its removal severely disrupts the target's ability to execute basic commands, compromising system operation.  
3. **LUA-based DoS Attack:** Using Redis's EVAL command, we execute a malicious Lua script designed to consume excessive memory. The Lua script contains an extremely long string, which, when processed by Redis, will cause excessive memory consumption. As a result, Redis will be terminated by the operating system due to resource exhaustion.  

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

The following Linux packages are required for the attack:  
    - `hydra`  
    - `openssh-client`  
    - `redis`  

To install these packages, run the following command:  
```bash
sudo apt install hydra openssh-client redis
```

## Attack Execution
To execute the attack, run the following command:   
```bash
./exploit.sh 
```

Alternatively, you can run the attack in non-interactive mode using:
```bash
./exploit.sh -all <Target IP Address> <Dictionary Name> <Attack Mode>
```
The specified dictionary file must be located in the `dictionary/` directory. For the attack mode, as previously mentioned, there are three different attacks that can be executed on the target system. You must choose one of the following options:  
    - `S` for the SSH Key Injection Attack  
    - `B` for the BusyBox Deletion Attack  
    - `L` for the LUA-based DoS Attack  

## System Restoration
To restore the system to its state prior to the attack, execute the following command:  
```bash
./restoration.sh <Target IP Address> <Attack Mode>
```

## MITRE ATT&CK Techniques List
The following tables lists the MITRE ATT&CK for ICS techniques used in each of the attacks:

### SSH Key Injection Attack:
| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0807        | Command-Line Interface   |The Redis command-line interface is used to execute commands on the Redis server. |
| T0859        | Valid Accounts           |Valid Redis credentials are used to access the Redis server.                      | 
| T0886        | Remote Services          |The Redis service is used to gain initial access to the target system.            |

### BusyBox Deletion Attack:
| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0807        | Command-Line Interface   |The Redis command-line interface is used to execute commands on the Redis server. |  
| T0809        | Data Destruction         |The goal of the attack is to delete the BusyBox binary from the target system.    |  
| T0814        | Denial of Service        |Removing BusyBox disrupts essential services, leading to a denial of service.     |  
| T0859        | Valid Accounts           |Valid Redis credentials are used to access the Redis server.                      | 
| T0881        | Service Stop             |Deleting BusyBox causes the Redis service to stop.                                |  
| T0886        | Remote Services          |The Redis service is used to gain initial access to the target system.            |

### LUA-based DoS Attack:
| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0804        | Block Reporting Message  |Sensor data are not forwarded to the IoT server after the Redis server is disrupted.     |  
| T0807        | Command-Line Interface   |The Redis command-line interface is used to execute commands on the Redis server.        |    
| T0814        | Denial of Service        |The goal of the attack is to perform a DoS on the Redis server.                          |  
| T0853        | Scripting                |A malicious Lua script is used to perform the DoS.                                       |  
| T0859        | Valid Accounts           |Valid Redis credentials are used to access the Redis server.                             | 
| T0866        | Exploitation of Remote Services |A vulnerability in Redis is exploited by sending a large string to exhaust memory.|  
| T0881        | Service Stop             |The Redis process is terminated by the operating system due to resource exhaustion.      |  
| T0886        | Remote Services          |The Redis service is used to gain initial access to the target system.                   |

> [!NOTE]
> Those table are based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
