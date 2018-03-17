'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''
import urllib.request
import json
import codecs


DOMO_IP = "192.168.1.100"
DOMO_PORT = "8050"

def domoticz_getJson(idx):
    url = "http://"+DOMO_IP+":"+DOMO_PORT+"/json.htm?type=devices&rid="
    req = urllib.request.Request(url+str(idx))
    response = urllib.request.urlopen(req)
    reader = codecs.getreader("utf-8")
    data = json.load(reader(response))
    return data

def domoticz_set_value(idx,value):
    url = "http://"+DOMO_IP+":"+DOMO_PORT+"/json.htm?type=command&param=udevice&idx="+str(idx)+"&nvalue=0&svalue="+str(value)
    req = urllib.request.Request(url)
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
    
def print_raw_json(status_idx):
    print(json.dumps(status_idx, indent=4, sort_keys=True))

def read_temp(idx):
    status_idx = domoticz_getJson(idx)
    try:
        dev_temp = status_idx["result"][0]["Temp"]
        return dev_temp
    except:
        return -255
    
def read_SetPoint(idx):
    status_idx = domoticz_getJson(idx)
    try:
        dev_temp = status_idx["result"][0]["SetPoint"]
        return dev_temp
    except:
        return -255
    
def set_temp(idx,value):
    status_idx = domoticz_set_value(idx, value)    
    try:
        dev_status = status_idx["status"]
        if dev_status == "OK":
            return True
        else:
            return False
    except:
        return False
    
