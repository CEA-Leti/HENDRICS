# SSH Adversary in the Middle Attack 

## Attack Overview
In this scenario, you are an attacker who has gained access to a local network. The objective of this attack is to identify SSH servers on the network and perform a Adversary-in-the-Middle (AiTM) attack to intercept credentials and traffic between SSH clients and a selected SSH server.

To carry out the attack, we proceed as follows:   
1. **Network Scanning:** We begin by scanning the network using `nmap` to identify hosts with port 22 (SSH) open. This allows us to enumerate potential SSH servers on the network.  
2. **Target Selection:** From the discovered hosts, we select one machine to act as the target SSH server. We also select one or more machines that are likely to act as SSH clients communicating with the server.  
3. **Start SSH MITM Server:** On the attacker’s machine, we start the [ssh-mitm](https://github.com/jtesta/ssh-mitm.git) server. This tool acts as an intermediary between the SSH client and the real SSH server, enabling real-time credential capture and traffic logging.
4. **ARP Spoofing:** Using Ettercap, we perform ARP spoofing between the chosen SSH clients and the target SSH server. This redirects all traffic through the attacker's machine, allowing ssh-mitm to intercept the communication.

## Requirements
Before running the attack, you MUST have the testbed installed.
See the [installation guide](../../embedded-device/README.md) to install the testbed.

The following Linux packages are required for the attack:  
    - `nmap`  
    - `ettercap`  
    - `openssh-client`   

To install these packages, run the following command:   
```bash
sudo apt install nmap ettercap-text-only openssh-client git
```

Then, clone and install the ssh-mitm project:
```bash
git clone https://github.com/jtesta/ssh-mitm.git
cd ssh-mitm/
git checkout 70998ba1b671268b641c2081d519107bf62cfa42
sudo ./install.sh
cd ..
```

> Warning: The attacker's machine must have a different IP address from that of the targeted SSH client. So you can't run the SSH client and the attacker on the same machine, unless you are using virtual machines. If using a virtual machine for the attacker, ensure it is configured in bridged mode or similar, allowing it to be on the same Layer 2 network as the target devices. ARP spoofing relies on Layer 2 access, so setups using NAT or host-only adapters may not work.

> Warning: For this attack to succeed, the target device must be able to reach the [MQTT broker's machine](../../servers/README.md). If the broker's machine is not accessible, the device will repeatedly attempt to locate it, sending numerous ARP broadcast requests in the process. This behavior causes the target to constantly update its ARP table with legitimate responses to the broadcasts, which can override the spoofed ARP entries. As a result, the ARP spoofing attack may fail to maintain control over the target’s ARP table. To avoid this issue, you can also stop the "mqtt_publisher.py" on the target device.

## Attack Execution
To execute the attack, run the following command:   
```bash
sudo ./exploit.sh 
```

Alternatively, you can run the attack in non-interactive mode using:  
```bash
sudo ./exploit.sh -all <Network range> <SSH Server IP Address> <SSH Client IP Address> 
```

Captured credentials will be logged in the `/var/log/auth.log` file. Additionally, the full exchange between SSH clients and the server will be recorded in `/home/ssh-mitm/log/`.

> Note: No system restoration is required after this attack.

## Triggering an SSH Connection
To facilitate testing, a Python server runs on the SCADA machine, listening on port 9000 at the `/ssh_connection` endpoint. You can use this endpoint to trigger an SSH connection from the SCADA system to the targeted SSH server. Use the following command to initiate the connection:
```bash
curl "http://<Scada IP Adresse>:9000/ssh_connection?ip_address=<SSH Server IP Adresse>&username=<SSH Username>&password=<SSH Password>"
```

> Note: The <SSH Client IP Address> parameter used in the attack must correspond to the SCADA machine’s IP address. Otherwise, ARP spoofing won’t redirect traffic from the SCADA machine, so the SSH connection it initiates to the SSH server will not be intercepted by the AiTM attack.

## MITRE ATT&CK Techniques List
The following table lists the MITRE ATT&CK for ICS techniques used in each of the attacks:

| Technique ID | Technique Name           | Justification                            |
|--------------|--------------------------|------------------------------------------|
| T0830        | Adversary-in-the-Middle  |The goal of the attack is to perform an Adversary-in-the-Middle attack.      | 
| T0842        | Network Sniffing         |ARP spoofing is used to intercept packets between the SSH client and server. | 
| T0846        | Remote System Discovery  |The attack starts by scanning the network to discover SSH servers to target. | 
| T0848        | Rogue Master             |The attacker assumes the role of a rogue master by intercepting communication between the client and server. | 
| T0859        | Valid Accounts           |The attacker steals valid SSH credentials to gain access to the target system.                               | 

> Note: Those table are based on [MITRE ATT&CK for ICS v17](https://attack.mitre.org/versions/v17/matrices/ics/).
