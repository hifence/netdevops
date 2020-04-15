import requests
import ipaddress
import exchangelib as E
import sys
import email
import requests
import json
import re
import time

librenms_api = "http://10.100.1.250/api/v0"
TOKEN = "b4a007698383ca1338368879f236eaf1"

headers = {'User-Agent': 'LibreNMS',
           'X-Auth-Token': TOKEN
           }


def is_ISP1(ipaddress):
    ISP1 = {
        "109.166.156.94" : ("58009", "Loc. Boldesti-Scaieni, Sos. Ploiesti-Valeni Nr.16,	Boldesti-Scaeni, Prahova"),
        "93.122.171.218" : ("61038", "sat Pleasa, strada principala - fosta ferma piscicola - este un zid alb cu o poarta,Pleasa, Prahova"),
        "93.122.145.46" : ("ID","Florica Romalo 4, Chitorani 107112, Judetul Prahova" ),
        "109.166.150.38" : ("58010","Bariera Traian,Str.Cetatianu Ioan,Nr.7,Hala - Galati, Galati"),
        "109.166.150.182" : ("58006","Str Orastie Nr 10 (cladire alaturata) - Cluj,Cluj-Napoca"),
        "109.166.150.174" : ("58009","Ecologistilor, Nr. 21	- Jud. Brasov, Sacele"),
        "109.166.149.146" : ("58007","Str.Aviatorilor Nr.12 (Parcul Industrial), Jud. Dolj, Craiova"),
        "109.166.149.254" : ("58008","Str. Caraiman, nr.15, pavilion H, 900117 - Jud. Constanta, Constanta"),
        "109.166.149.130" : ("58004","Com. Holboca, Nr.615, Jud. Iasi, Holboca" ),
        "109.166.149.206" : ("58005", "Ortisoara, Strada Principala, Nr. 282/A, Jud. Timis")
    }

    if  ipaddress in ISP1.keys():
        service_id = ISP1[ipaddress][0]
        location = ISP1[ipaddress][1]
        return service_id,location
    else: return False


def is_ISP3(ipaddress):
    ISP3 = {
    "109.166.156.94" : ("58009", "Loc. Boldesti-Scaieni, Sos. Ploiesti-Valeni Nr.16,	Boldesti-Scaeni, Prahova"),
    "5.2.209.40" : ("XXX" , "Bariera Traian,Str.Cetatianu Ioan,Nr.7,Hala - Galati, Galati"),
    "5.2.182.133" : ("291668099","Chitorani, Strada Florica Romalo, Nr. 4" ),
    "5.2.239.136" : ("XXX","Poiana Tapului"),
    "86.120.135.136" : ("271511408","Bucuresti, Sector 1, Bulevard Bucurestii Noi, Nr. 140"),
    "5.2.193.168" : ("271511393","Cluj-Napoca, Strada Orastiei, Nr. 10, Bl. depozit 26, Sc. -, Et. , Ap."),
    "82.77.64.197" : ("271511402","Ghercesti, Strada Aviatorilor, Nr. 10"),
    "5.2.230.21" : ("271511392","Constanta, Strada Caraiman, Nr. 15" ),
    "5.2.181.56" : ("271511398","Filipestii de Padure, Strada Garii, Nr. 661"),
    "5.2.191.206" : ("271511395","Iasi, Strada Holboca, Nr. 615"),
    "5.2.156.78" :  ("271511401","Mogosoaia, Sosea Bucuresti-Targoviste, Nr. 1A, Bl. CrisTim2"),
    "5.2.181.15" : ("271511406","Loc. Boldesti-Scaieni, Sos. Ploiesti-Valeni Nr.16,	Boldesti-Scaeni, Prahova"),
    "86.125.115.195" : ("271511403","Ortisoara, Strada Principala, Nr. 282/A, Jud. Timis")
    }
    if  ipaddress in ISP3.keys():
        service_id = ISP3[ipaddress][0]
        location = ISP3[ipaddress][1]
        return service_id,location
    else: return False


def is_ISP2(ipaddress):
    ISP2 = {
        "109.103.183.205" : ("METRONET 47204376","Chitorani, Strada Florica Romalo, Nr. 4"),
        "92.83.3.130" : ("METRONET 47203706","Filipestii de Padure"),
        "109.103.17.2" : ("METRONET 52492002","Bucuresti, Sector 1, Bulevard Bucurestii Noi, Nr. 140")
    }
    if  ipaddress in ISP2.keys():
        service_id = ISP2[ipaddress][0]
        location = ISP2[ipaddress][1]
        return service_id,location
    else: return False


def is_ISP4(ipaddress):
    ISP4 = {"92.85.91.166": ("","Mogosoaia, Sosea Bucuresti-Targoviste, Nr. 1A, Bl. CrisTim2")}
    if  ipaddress in ISP4.keys():
        service_id = ISP4[ipaddress][0]
        location = ISP4[ipaddress][1]
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
    creds = E.Credentials(username='casiopea.new\\noc', password='aaIv5EInx2LCtZQQGzrZ')
    config = E.Configuration(server='webmail.cristim.ro', credentials=creds)
    a = E.Account(primary_smtp_address='noc@cristim.ro', config=config, autodiscover=False, access_type=E.DELEGATE)
    m = E.Message(
        account=a,
        subject='Router Down',
        body=email_body,
        to_recipients=email_isp,
        cc_recipients=['dispecerat.cristim@cristim.ro', 'HelpDeskCristim@cristim.ro'],  # Simple strings work, too
        #cc_recipients=['daniel.sarica@cristim.ro', 'marcel.grapinoiu@cristim.ro','dispecerat.cristim@cristim.ro', 'HelpDeskCristim@cristim.ro'],
        bcc_recipients=["daniel.sarica@gmail.com", 'marcel.grapinoiu@outlook.com'],  # Or a mix of both
    )
    m.send_and_save()



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
                    proximus.delete()
                    return j
        

get_alert_ip = check_email()
device_id = query_ip(get_alert_ip)
public_ip = get_all_ips(device_id)
print(public_ip)

if is_ISP1(public_ip):
    email_isp = ["arssuprt@orange.com","supervizare@orange.ro"]
    service_id,location = is_ISP1(public_ip)
    send_alert_email(public_ip, service_id, location, email_isp)  
    print("Este IP ISP1")
if is_ISP2(public_ip):
    email_isp = ["bsc_suport_date@telekom.ro", "bsc_premium@telekom.ro"]
    service_id,location = is_ISP2(public_ip)
    send_alert_email(public_ip, service_id, location, email_isp)  
    print("Este IP Tlk")
if is_ISP3(public_ip):
    email_isp = ["suport@rcs-ISP3.ro"]
    service_id,location = is_ISP3(public_ip)
    send_alert_email(public_ip, service_id, location, email_isp)    
    print("Este IP RDS")
if is_ISP4(public_ip):
    email_isp = ["daniel.sarica@gmail.com"]
    service_id,location = is_ISP4(public_ip)
    send_alert_email(public_ip, service_id, location, email_isp)  
    print("Este IP PRIME")