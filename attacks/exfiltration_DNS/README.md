# Data Exfiltration Via DNS

## Attack Overview
In this scenario, you are an attacker who has gained access to a PLC (Programmable Logic Controller) due to the use of default credentials (`openplc`:`openplc`). The goal of this attack is to exfiltrate the PLC logic via DNS packets.

To carry out the attack, we proceed as follows:  
1. **Upload Malicious Script :** First, we authenticate and upload a Bash script to the OpenPLC server as if it were a new PLC program. This script is designed to read the current PLC logic and encode its contents into DNS queries.
2. **Modify the OpenPLC Driver :** Next, we modify the OpenPLC driver. The OpenPLC driver is a program that runs before the PLC logic starts, and is normally used to handle inputs and outputs at hardware layer. The modified driver includes instructions to run the previously uploaded Bash script.
3. **Set Up the DNS Server :** On the attacker's machine, we set up a DNS server named [DNSteal](https://github.com/m57/dnsteal.git). This server will capture and reconstruct the exfiltrated data from the DNS packets sent by the Bash script.
4. **Restart the PLC Program :** Finally, we restart the PLC program, which will execute the modified driver. This in turn triggers the Bash script, initiating the exfiltration process by transmitting the encoded data via DNS queries to the attacker’s DNS server.

The Python script used for orchestrating this attack is sourced from [Exploit-DB](https://www.exploit-db.com/exploits/49803).

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

You also need to install Python and Git. You can install them with the following command:  
```bash
sudo apt install python3 python3-pip git
```

Additionally, you’ll need the 'requests' Python library. You can install it by running:
```bash
pip install requests==2.25.1
```

## Attack Execution
To execute the attack, run the following command:  
```bash
sudo ./exploit.sh 
```

Alternatively, you can run the attack in non-interactive mode using:  
```bash
sudo ./exploit.sh -all <Target IP Address> 
```

## System Restoration
To restore the system to its state prior to the attack, execute the following command:  
```bash
python3 restoration.py <Target IP Address> 
```

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in this attack:  

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0809        | Data Destruction          |After data exfiltration is complete, the script used for exfiltration is removed. |
| T0812        | Default Credentials       |The attacker authenticates using the default OpenPLC credentials.                 |
| T0823        | Graphical User Interface  |The attack script communicates with the OpenPLC by replicating the exact same requests and steps a user would perform through the OpenPLC graphical interface.  |
| T0843        | Program Download          |A malicious Bash script is transfered to the OpenPLC server.                      |
| T0845        | Program Upload            |The goal of this attack is to retrieves the PLC logic from the target system.     | 
| T0853        | Scripting                 |A Bash script is used to exfiltrate the PLC logic via DNS queries.                |
| T0858        | Change Operating Mode     |The OpenPLC driver is modified to execute a Bash script before running the PLC logic. |
| T0869        | Standard Application Layer Protocol |The DNS protocol is used to exfiltrate data to the attacker server.         |
| T0872        | Indicator Removal on Host |After data exfiltration is complete, the script used for exfiltration is removed.     |
| T0885        | Commonly Used Port        |Port 53 (DNS) is used for exfiltration to evade network security monitoring.          |
| T0886        | Remote Services           |The OpenPLC service is used to gain initial access to the target system.              |
| T0889        | Modify Program            |The OpenPLC driver program is altered to execute a malicious Bash script.             |

> [!NOTE]
> This table is based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).


