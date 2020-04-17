import requests
import ipaddress
import exchangelib as E
import sys
import email
import requests
import json
import re
import time

librenms_api = "http://IP_ADDRESS/api/v0"
TOKEN = "TOKEN"
exchange_username = "domain\\username"
exchange_password = "username_password"
exchange_server = "webmail.example.com"
exchange_smtp_address = "username@example.com"
exchange_cc_recipients= ['noc@example.com','helpdesk@example']

email_ISP1 = ['email1@isp1.com','email2@isp1.com']
email_ISP2 = ['email1@isp2.com','email2@isp2.com']
email_ISP3 = ['email1@isp3.com','email2@isp3.com']


headers = {'User-Agent': 'LibreNMS',
           'X-Auth-Token': TOKEN
           }


def is_ISP1(ipaddress):
    ISP1 = {
        #Example Usage: "IP" : ( "ServiceID", "Location" )
    "1.1.1.1" : ("SERVICEID" , "Manhattan, New York"),
    "1.1.1.2" : ("SERVICEID" , "Manhattan, New York"),
    }

    if  ipaddress in ISP1.keys():
        service_id = ISP1[ipaddress][0]
        location = ISP1[ipaddress][1]
        return service_id,location
    else: return False

def is_ISP2(ipaddress):
    ISP2 = {
        #Example Usage: "IP" : ( "ServiceID", "Location" )
    "2.1.1.1" : ("SERVICEID" , "Manhattan, New York"),
    "2.1.1.2" : ("SERVICEID" , "Manhattan, New York"),
    }
    if  ipaddress in ISP2.keys():
        service_id = ISP2[ipaddress][0]
        location = ISP2[ipaddress][1]
        return service_id,location
    else: return False

def is_ISP3(ipaddress):
    ISP3 = { 
        #Example Usage: "IP" : ( "ServiceID", "Location" )
    "3.1.1.2" : ("SERVICEID" , "Manhattan, New York"),
    "3.1.1.2" : ("SERVICEID" , "Manhattan, New York"),

    }
    if  ipaddress in ISP3.keys():
        service_id = ISP3[ipaddress][0]
        location = ISP3[ipaddress][1]
        return service_id,location
    else: return False




def query_ip(query_ip):
    query_url = librenms_api + "/devices?type=ipv4&query=" + \
        str(query_ip)
    r = requests.get(query_url, headers=headers)
    json = r.json()
    device_id = json["devices"][0]["device_id"]
    print(device_id)
    return device_id


def get_all_ips(device_id):
    ip_url = librenms_api + "/devices/" + str(device_id) + "/ip"
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


def send_alert_email(public_ip, service_id, location, email_isp):
    email_body = "Buna ziua, \n Nu ne mai raspunde routerul cu IP-ul: " + public_ip + "\n ServiceID: " + service_id + "\n Locatie: " + location + "\n Ne puteti ajuta va rugam cu o verificare ? \n P.S.: Va rugam sa raspundeti cu toti colegii din CC.\n O zi buna, \n NOC Team \n"
    creds = E.Credentials(username=exchange_username, password=exchange_password)
    config = E.Configuration(server=exchange_server, credentials=creds)
    a = E.Account(primary_smtp_address=exchange_smtp_address, config=config, autodiscover=False, access_type=E.DELEGATE)
    m = E.Message(
        account=a,
        subject='Router Down',
        body=email_body,
        to_recipients=email_isp,
        cc_recipients=exchange_cc_recipients,  # Simple strings work, too
    )
    m.send_and_save()



def check_email():
    creds = E.Credentials(username=exchange_username, password=exchange_password)
    config = E.Configuration(server=exchange_server, credentials=creds)
    account = E.Account(primary_smtp_address=exchange_smtp_address, config=config, autodiscover=False, access_type=E.DELEGATE)  # logging onto Exchange
    email_filtered = account.inbox.filter(subject__icontains="Devices up/down")
    re_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")				
    if email_filtered.exists():  # if there are any e-mails for this filter
        for i in email_filtered:			# for each e-mail
            #print(i.body)
            ip = re.findall(re_ip,i.body)
            for j in ip:
                if not None:
                    email_filtered.delete()
                    return j
        

get_alert_ip = check_email()
device_id = query_ip(get_alert_ip)
public_ip = get_all_ips(device_id)
print(public_ip)

if is_ISP1(public_ip):
    email_isp = email_ISP1
    service_id,location = is_ISP1(public_ip)
    send_alert_email(public_ip, service_id, location, email_isp)  
    print("Sending Email to ISP1")
if is_ISP2(public_ip):
    email_isp = email_ISP2
    service_id,location = is_ISP2(public_ip)
    send_alert_email(public_ip, service_id, location, email_isp)  
    print("Sending Email to ISP2")
if is_ISP3(public_ip):
    email_isp = email_ISP3
    service_id,location = is_ISP3(public_ip)
    send_alert_email(public_ip, service_id, location, email_isp)    
    print("Sending Email to ISP3")