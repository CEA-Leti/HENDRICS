## AiTM Attack via Modbus TCP

## Attack Overview
In this scenario, you are an attacker who has access to a machine within the same network as the SCADA system and the Programmable Logic Controller (PLC). The goal of this attack is to perform an Adversary-in-the-Middle (AiTM) attack, enabling the manipulation of the physical process controlled by the PLC, while keeping the SCADA system unaware of any malicious activity.

To carry out the attack, we proceed as follows:
1. **Perform ARP Spoofing:** First, we launch an ARP spoofing attack to position ourselves between the SCADA system and the PLC. This allows us to intercept and monitor all Modbus TCP traffic between the two devices. During this phase, we record legitimate communication messages exchanged between the SCADA and the PLC.
2. **Replay Recorded Traffic:** After a certain time, we stop recording and begin replaying the captured Modbus messages in a continuous loop. This creates the illusion of normal behavior. At the same time, we block any new messages from the SCADA to the PLC. This ensures that any commands issued by the SCADA will not reach the PLC, and any real-world changes made by the attacker will not be visible on the SCADA interface.
3. **Inject Malicious Commands:** With the SCADA blinded, we are now free to send our own Modbus commands directly to the PLC. For example, we can overwrite coil values to change actuator states or manipulate the physical process in other ways, completely hidden from the operator’s view.

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

To carry out this attack, Ettercap and Python are required. You can install them by running the following command:
```bash
sudo apt install ettercap-text-only python3
```

After installing Ettercap, configure it by editing the configuration file located at `/etc/ettercap/etter.conf`. Modify the `ec_uid` and `ec_gid` fields as follows:
```
ec_uid = 0                # nobody is the default
ec_gid = 0                # nobody is the default
```

> [!CAUTION]
> The attacker machine must have a different IP address than the SCADA server. So you can't run the SCADA server and the attacker on the same machine, unless you are using virtual machines. If using a virtual machine for the attacker, ensure it is configured in bridged mode or similar, allowing it to be on the same Layer 2 network as the target devices. ARP spoofing relies on Layer 2 access, so setups using NAT or host-only adapters may not work.

> [!CAUTION]
> For this attack to succeed, the target device must be able to reach the [MQTT broker's machine](../../servers/README.md). If the broker's machine is not accessible, the device will repeatedly attempt to locate it, sending numerous ARP broadcast requests in the process. This behavior causes the target to constantly update its ARP table with legitimate responses to the broadcasts, which can override the spoofed ARP entries. As a result, the ARP spoofing attack may fail to maintain control over the target’s ARP table. To avoid this issue, you can also stop the "mqtt_publisher.py" on the target device.

## Attack Execution
To execute the attack, run the following command:  
```bash
sudo ./exploit.sh 
```

Alternatively, you can run the attack in non-interactive mode using:  
```bash
sudo ./exploit.sh -all <PLC IP Address> <Scada IP Address> <Loop Duration>
```

## System Restoration
To restore the system to its state prior to the attack, execute the following command:  
```bash
./restoration.sh <OpenPLC IP Address> <Physical Process IP Address>
```

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in this attack:  

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0801        | Monitor Process State    |By capturing network traffic between the PLC and SCADA, we gains insight into the physical process state. | 
| T0803        | Block Command Message    |All messages sent from the SCADA system to the PLC are block to prevent control.           | 
| T0804        | Block Reporting Message  |Messages sent by the PLC to the SCADA system are replace with previously recorded ones.    | 
| T0806        | Brute Force I/O          |By manipulating coil values, the attacker can control physical processes (e.g., start or stop machinery). | 
| T0830        | Adversary-in-the-Middle  |ARP spoofing is used to perform a Adversary-in-the-Middle attack.                          | 
| T0836        | Modify Parameter         |By manipulating coil values, the attacker can modify some PLC logic parameters.            | 
| T0842        | Network Sniffing         |The attack begins by monitoring traffic exchanged between the SCADA system and PLC.        | 
| T0848        | Rogue Master             |The attacker assumes the role of a rogue master and sends commands to the PLC.             | 
| T0855        | Unauthorized Command Message |The attacker can sends any commands to the PLC.                                        | 
| T0856        | Spoof Reporting Message      |Messages sent by the PLC to the SCADA system are replace with previously recorded ones.| 
| T0878        | Alarm Suppression            |Messages sent by the PLC to the SCADA system are replace with previously recorded ones.| 

> [!NOTE]
> This table is based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
