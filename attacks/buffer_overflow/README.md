# Buffer Overflow for Privilege Escalation

## Attack Overview
In this scenario, you are an attacker with low-privileged access to a target system. The goal of this attack is to escalate privileges by exploiting a buffer overflow vulnerability in a SUID (Set User ID) binary, ultimately gaining a root shell.

The SUID bit allows any user to execute a binary with the permissions of its owner. In this case, the owner is root. By leveraging a vulnerability in such a binary, it becomes possible to execute arbitrary code with elevated privileges.

To carry out the attack, we proceed as follows:  
1. **Inject Shellcode:** We start by placing a shellcode that spawns a root shell into an environment variable. This allows the shellcode to be loaded onto the stack when the vulnerable binary is executed.
2. **Exploit the Buffer Overflow:** Next, we perform a buffer overflow on the vulnerable binary to overwrite its return address, redirecting execution flow to our shellcode.  
3. **Spawning a Root Shell:** Once the buffer overflow successfully redirects execution, the shellcode is triggered, spawning a root shell and granting full control over the system.

For the attack to work smoothly, the following conditions must be met:  
- ASLR (Address Space Layout Randomization) must be disabled on the target.  
- The binary must have an executable stack.  
- The binary must not have stack-smashing protection enabled.  

This attack is inspired by the [RootMe challenge](https://www.root-me.org/fr/Challenges/App-Systeme/ELF-x86-Format-String-Bug-Basic-3) "ELF x86 - Format String Bug Basic 3"

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

The following Linux packages are required for the attack:  
    - `openssh-client`  
    - `sshpass`  

To install these packages, run the following command:
```bash
sudo apt install openssh-client sshpass
```

## Attack Execution
To execute the attack, run the following command:  
```bash
./exploit.sh 
```

If you prefer, to execute the attack in non-interactive mode, specify the target's IP address and credentials:  
```bash
./exploit.sh -all <Target IP Address> -p <Low-Privileged Username> <Low-Privileged Password>
```

Alternatively, you can use SSH keys instead of a password:  
```bash
./exploit.sh -all <Target IP Address> -k <Low-Privileged Username> <Path to SSH Key File>
```

## System Restoration
To restore the system to its state prior to the attack, execute the following command:  
```bash
./restoration.sh <Target IP Address> <Low-Privileged Username>
```
> [!NOTE]
> The username must be the same as the one used during the attack.

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in this attack:  

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0807        | Command-Line Interface                |The target system's command-line interface is used to perform the buffer overflow. |
| T0853        | Scripting                             |A Python script is used to export the shellcode as an environment variable. |  
| T0890        | Exploitation for Privilege Escalation |The goal of this attack is to gain root access.                             |

> [!NOTE]
> This table is based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
