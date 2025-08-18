# RCE OpenPLC

## Attack Overview
In this scenario, you are an attacker who has gained access to a PLC (Programmable Logic Controller) due to the use of default credentials (`openplc`:`openplc`). The goal of this attack is to escalate privileges by doing some Remote code execution on the PLC, ultimately gaining a root revershell.

To carry out the attack, we proceed as follows:  
1. **Set Up a Netcat Listener:** On the attacker’s machine, we set up a Netcat listener to receive the incoming reverse shell connection from the target PLC device.
1. **Modify the OpenPLC Driver:** Next, we modify the OpenPLC driver. The OpenPLC driver is a program that runs before the PLC logic starts, and is normally used to handle inputs and outputs at hardware layer. The modified driver includes instructions to initiate a reverse shell connection back to our Netcat listener.
3. **Restart the PLC Program:** Finally, we restart the PLC program. Upon startup, the modified driver is executed, which triggers the reverse shell and grants the attacker remote root access to the device.

The Python script used for orchestrating this attack is sourced from [Exploit-DB](https://www.exploit-db.com/exploits/49803).

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

The following Linux packages are required for the attack:  
    - `python3`   
    - `konsole`    

To install these packages, run the following command:
```bash
sudo apt install python3 python3-pip konsole
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

Alternatively, you can run the attack in non-interactive mode using:
```bash
./exploit.sh -all <Target IP Address>
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
| T0812        | Default Credentials      |The attacker authenticates using the default OpenPLC credentials.          | 
| T0814        | Denial of Service        |As long as the reverse shell remains active, the PLC logic does not start. | 
| T0843        | Program Download         |A new OpenPLC driver is uploaded to the target system.                     | 
| T0853        | Scripting                |The modified OpenPLC driver is a Python script.                            | 
| T0858        | Change Operating Mode    |The OpenPLC driver is modified initiate a reverse shell connection before running the PLC logic. | 
| T0866        | Exploitation of Remote Services  | The OpenPLC web is exploited to achieve remote code execution.                          | 
| T0871        | Execution through API    |The attacke script communicates with the OpenPLC server via its REST API.                        | 
| T0886        | Remote Services          |The OpenPLC service is used to gain initial access to the target system.                         | 
| T0889        | Modify Program           |The OpenPLC driver is altered to initiate a reverse shell connection.                            | 

> [!NOTE]
> This table is based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
