import requests
import ipaddress
import exchangelib as E
import sys
import email
import requests
import json
import re
import time


headers = {'User-Agent': 'George',
           'X-Auth-Token': 'b4a007698383ca1338368879f236eaf1'
           }


def is_orange(ipaddress):
    ORANGE = ["109.166.156.94", "93.122.171.218", "93.122.145.46", "109.166.150.38", "109.166.150.182", "109.98.71.18", "109.166.150.174",
    "109.166.150.182", "109.166.149.146", "109.166.149.254", "109.166.149.130"]
    if ipaddress in ORANGE:
        return True
    else: return False


def is_rds(ipaddress):
    RDS = ["5.2.132.98", "5.2.128.61", "5.2.207.137", "5.2.135.193", "5.2.250.93", "5.2.206.239", "5.2.209.40", "5.2.158.125", "5.2.158.124", "5.2.216.58", "5.2.182.133", "5.2.239.136",
    "86.120.135.136", "82.76.45.12", "5.2.193.168", "82.77.64.197", "5.2.230.21", "5.2.181.56", "5.2.191.206", "5.2.156.78", "86.125.12.158", "5.2.180.22", "5.2.181.15",
    "86.125.115.195"]
    if ipaddress in RDS:
        return True
    else: return False


def is_telekom(ipaddress):
    TELEKOM = ["92.85.91.166", "109.103.183.205",
        "92.83.3.130", "109.98.71.18", "109.103.17.2"]
    if ipaddress in TELEKOM:
        return True
    else: return False


def is_prime(ipaddress):
    PRIME = "89.47.225.246"
    if ipaddress in PRIME:
        return True
    else: return False


def query_ip(query_ip):
    query_url = "http://10.100.1.250/api/v0/devices?type=ipv4&query=" + \
        str(query_ip)
    r = requests.get(query_url, headers=headers)
    json = r.json()
    device_id = json["devices"][0]["device_id"]
    print(device_id)
    return device_id


def get_all_ips(device_id):
    ip_url = "http://10.100.1.250/api/v0/devices/" + str(device_id) + "/ip"
    r = requests.get(ip_url, headers=headers)
    json = r.json()
    total_ips = len(json["addresses"])
    for i in range(total_ips):
        # print (json["addresses"][i]["ipv4_address"])
        ip_address = json["addresses"][i]["ipv4_address"]
        PUBLIC = ipaddress.ip_address(ip_address).is_private
        if PUBLIC is False:
            return ip_address
        else:
            return None






def check_email():
    creds = E.Credentials(username='casiopea.new\\noc', password='aaIv5EInx2LCtZQQGzrZ')
    config = E.Configuration(server='webmail.cristim.ro', credentials=creds)
    account = E.Account(primary_smtp_address='noc@cristim.ro', config=config, autodiscover=False, access_type=E.DELEGATE)  # logging onto Exchange
    proximus = account.inbox.filter(subject__icontains="Devices up-down")
    re_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")				#
    if proximus.exists():  # if there are any e-mails for this filter
        for i in proximus:			# for each e-mail
            #print(i.body)
            ip = re.findall(re_ip,i.body)
            for j in ip:
                if not None:
                    return j
        proximus.delete()


get_alert_ip = check_email()
device_id = query_ip(get_alert_ip)
public_ip = get_all_ips(device_id)
print(public_ip)

if is_orange(public_ip):
    print("Este IP Orange")
if is_telekom(public_ip):
    print("Este IP Tlk")
if is_rds(public_ip):
    print("Este IP RDS")
if is_prime(public_ip):
    print("Este IP Prime")