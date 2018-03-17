'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''
import urllib.request
import json
DOMO_IP = "192.168.1.100"
DOMO_PORT = "8050"

def domoticz_getJson(idx):
    url = "http://"+DOMO_IP+":"+DOMO_PORT+"/json.htm?type=devices&rid="
    req = urllib.request.Request(url+str(idx))
    response = urllib.request.urlopen(req)

    # Parse Json
    data = json.load(response)
    return data


def is_Switch_On(idx):
    status_idx = domoticz_getJson(idx)
    try:
        dev_status = status_idx["result"][0]["Status"]
        #print (json.dumps(switch_status, indent=4, sort_keys=True, ensure_ascii=False).encode('UTF-8'))
        if dev_status == "On":
            return True
        else:
            return False
    except:
        return False
    

dupa =  is_Switch_On(2132)

print(dupa)