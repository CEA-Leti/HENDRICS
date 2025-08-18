# SSH Dictionary Attack

## Attack Overview
In this scenario, you are an attacker who has discovered a target device with an SSH service protected by a weak password. The goal of this attack is to gain access to the target device through a dictionary attack.

To achieve this, the we use the `hydra` tool to launch a dictionary attack against the SSH service. This brute-force method attempts various password combinations from a predefined wordlist until the correct password is found.  

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

The following Linux packages are required for the attack:  
    - `hydra`  
    - `openssh-client`  
    - `sshpass`   

To install these packages, run the following command:   
```bash
sudo apt install hydra openssh-client sshpass
```

## Attack Execution
To execute the attack, run the following command:   
```bash
./exploit.sh 
```

Alternatively, you can run the attack in non-interactive mode using:  
```bash
./exploit.sh -all <Target IP Address> <Dictionary Name> <SSH Username>
```
The dictionary file must be located in the `dictionary/` directory 

> [!NOTE]
> No system restoration is required after this attack.

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in each of the attacks:

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0859        | Valid Accounts           |Valid SSH credentials are used to access the target system.          | 
| T0886        | Remote Services          |The SSH service is used to gain initial access to the target system. |

> [!NOTE]
> Those table are based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
