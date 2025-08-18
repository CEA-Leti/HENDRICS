# Boopkit

## Attack Overview
In this attack scenario, you are an attacker who has already gained root privileges on the target machine. With root access, you've deployed a rootkit based on eBPF (Extended Berkeley Packet Filter) technology. The goal of this attack is to trigger the rootkit on the compromised system, which will then open a reverse shell, allowing further exploitation or remote control.

This rootkit, based on [Boopkit](https://github.com/krisnova/boopkit), operates at the kernel level using eBPF. It monitors TCP Reset packets and inspects them for embedded commands. When a command is detected, the rootkit executes it.

To trigger a reverse shell using Boopkit, we sends a crafted TCP Reset packet to port 22 on the target system. This packet contains a command that instructs the target to initiate a connection to a Netcat listener running on port 3545, thereby granting us a reverse shell.

<p align="center">
  <img src="https://user-images.githubusercontent.com/13757818/168698377-9c1125d6-698d-4009-a599-56b275b54764.jpeg" width="800"/>
</p>

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

The following Linux packages are required for the attack:  
    - `linux-tools-common`  
    - `linux-tools-<kernel_version>`  
    - `pahole`  
    - `konsole`  
    - `clang`  
    - `openssh-client`  
    - `sshpass`  

To install these packages, run the following command:
```bash
sudo apt install linux-tools-common linux-tools-$(uname -r) pahole konsole clang openssh-client sshpass git
```

## Attack Execution
Before executing the attack, Boopkit must already be running on the target machine. To start Boopkit, SSH into the target as root and use the following command:
 ```bash
/etc/boopkit -i end0 
```

Once Boopkit is running, execute the attack using the following command:
```bash
sudo ./exploit.sh 
```

Alternatively, you can run the attack in non-interactive mode using:
```bash
sudo ./exploit.sh -all <Target IP Address> <Root Username> <Root Password>
```

## System Restoration
To restore the system to its state prior to the attack, simply shut down Boopkit by running:
```bash
./restoration.sh <Target IP Address> <Root Username>
```
> [!NOTE]
> The username must be the same as the one used during the attack.

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in this attack:

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0807        | Command-Line Interface   |Boopkit is started using the target system’s command-line interface.   |
| T0834        | Native API               |eBPF uses Linux native API calls to filter and manipulate TCP packets. |
| T0851        | Rootkit                  |Boopkit operates as a rootkit, providing the attacker persistent access to the system.|  
| T0874        | Hooking                  |Boopkit uses eBPF to hook into the kernel and monitor network traffic.          |

> [!NOTE]
> This table is based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).




