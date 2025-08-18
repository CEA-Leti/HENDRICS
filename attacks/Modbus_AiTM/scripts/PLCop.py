# Copyright (C) 2025 CEA - All Rights Reserved
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import sys
import time
import re

OPENPLC_USERNAME="openplc"
OPENPLC_PASSWORD="openplc"
OPENPLC_WEBSERVER_PORT="8080"

openplc_url = "http://" + sys.argv[1] + ":"+ OPENPLC_WEBSERVER_PORT
login_url = openplc_url + '/login' 
action_url = openplc_url + "/" + sys.argv[2]

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


def auth():
    print('[+] Checking if host '+ openplc_url +' is up...')
    send_request("GET", login_url)
    print('[+] Host is up and reachable.')

    print('[+] Trying to authenticate with credentials '+ OPENPLC_USERNAME +':'+ OPENPLC_PASSWORD +'...')   
    credentials = {
        'username': OPENPLC_USERNAME,
        'password': OPENPLC_PASSWORD
    }

    login_response = send_request("POST", login_url, None, None, credentials)
    match = re.search(r"<div class='login-page'>", login_response.text)

    if (login_response.status_code == 200 and not match):
        print('[+] Login successful.')
    else:
        print('[!] Login failed.')
        print('Please check your credentials and try again.')
        print('If the credentials are correct, the issue could be that the target system\'s time is out of sync.')
        print('This issue may occur if the target system was powered off or has incorrect time settings.')
        print('To fix this, navigate to /embedded-device/scripts_config and run the "update_timedate.sh" script to update the system time.')
        sys.exit(1)  
  

auth()
send_request("GET", action_url)
