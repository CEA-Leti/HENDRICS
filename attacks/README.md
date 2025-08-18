# Testbed Attack Guide

## Overview
This directory contains a collection of attack scenarios developed for the [HENDRICS testbed](../README.md). Each scenario simulates a realistic threat vector found in embedded devices, industrial control systems or IoT environments, according to the [MITRE ATT&CK for ICS Matrix](https://attack.mitre.org/versions/v17/matrices/ics/). 

> [!NOTE]
> All attacks have been developed and tested to be executed from an Ubuntu 22.04 (64-bit) machine. Compatibility with other attack environments has not been verified.

## Available Attacks

| Attack Title        | Description                                               |
|---------------------|-----------------------------------------------------------|
| [Boopkit](./Boopkit/README.md)                     | Installs an eBPF-based rootkit that listens for special TCP packets to trigger a reverse shell.    | 
| [Buffer Overflow](./buffer_overflow/README.md)     | Exploits a vulnerable SUID binary to execute shellcode and escalate privileges.                    |
| [Exfiltration DNS](./exfiltration_DNS/README.md)   | Exfiltrates PLC logic by encoding and sending it over DNS requests.                                |
| [Exfiltration ICMP](./exfiltration_ICMP/README.md) | Exfiltrates files using ICMP packets by hijacking a Redis backup script.                           |
| [Mirai Malware](./Mirai_malware/README.md)         | Infects the device with Mirai malware, enabling it to propagate and launch DDoS attacks.           |
| [Modbus AiTM](./Modbus_AiTM/README.md)      | Intercepts and modifies Modbus traffic between SCADA and PLC to stealthily control the physical process.  |
| [Path Exploitation](./path_exploitation/README.md)         | Gains root access by exploiting PATH manipulation in a vulnerable SUID binary.             |
| [RCE OpenPLC](./RCE_OpenPLC/README.md)      | Achieves privilege escalation by modifying an OpenPLC driver to spawn a root shell.                       |
| [Redis Global Attack](./Redis_global_attack/README.md)     | Combines three attacks in one: Brute-forces Redis credentials and enables actions like SSH access, DoS, or file deletion. |
| [Redis Lua Injection](./Redis_Lua_injection/README.md)     | Injects Lua code through a vulnerable endpoint to execute commands on Redis.               |
| [SSH Dictionary Attack](./SSH_dictionary_attack/README.md) | Performs brute-force attacks against SSH to gain access and deploy a payload.              |
| [SSH AiTM](./SSH_AiTM/README.md)                           | Captures SSH credentials by intercepting traffic through a adversary-in-the-middle proxy.        |

## Attack Execution Modes
Each attack includes three execution modes to suit different use cases and levels of expertise:  
1. **Step-by-Step Mode:** The user is guided through each step of the attack, with detailed explanations of how it works.  
2. **Interactive Mode:** The script prompts the user for necessary input values and performs the attack with minimal manual intervention.  
3. **Non-Interactive Mode:** All required parameters are passed as arguments. The attack executes fully automatically, making it ideal for scripting.

## Disclaimer
The vulnerabilities exploited in this testbed are publicly known and listed as Common Vulnerability Exposures (CVE), meaning that potentially affected parties have already been informed and advised to mitigate risks. The attacks presented in this repository, along with their source code, are intended to be used only on this testbed, for educational and research purposes.  

> [!CAUTION]
> The deployment of certain attacks such as Mirai can generate substantial network traffic and pose risks to connected devices. We strongly recommend setting up this testbed on a closed and isolated network to avoid impacting other systems.

## License
This module is part of the HENDRICS testbed and is subject to the same license terms.  
Please refer to the [LICENSE](../LICENSE) file located at the root of the repository.
