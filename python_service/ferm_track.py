# Based on https://github.com/atlefren/pytilt/blob/master/pytilt.py

# TODO UPDATE REFERENCES/SOURCES - ADD README
# Ambient sensor: https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/
# send to queue/sb/whatever
# https://blog.softhints.com/python-convert-object-to-json-3-examples/#built


import sys
import datetime
import time
import threading
import subprocess
import json
import bluetooth._bluetooth as bluez
import blescan
import Adafruit_DHT
import adascreen
import fermdatapoint
import requests
from copy import copy
#from azure.servicebus import ServiceBusClient, ServiceBusMessage

#lol hardcoded
#CONNECTION_STR = 
#QUEUE_NAME = "brewing-update"

# DHT Sensor Type
sensor = Adafruit_DHT.DHT22
gpio_pin = 26 # I think this is GPIO pin not literal pin #

#aggregation stuff
dpList = []

CURRENT_BEER_NAME = "TestBeer1"
SHEETS_SCRIPT = "<insert here>"

def ScreenLoop(fermdp):
    while True:
        update_diff = (datetime.datetime.now() - fermdp.getTimestamp()).seconds
        adascreen.drawDataPoint(fermdp.getColor(), fermdp.getGravity(), fermdp.getFermTemp(), fermdp.getAmbTemp(), update_diff)
        time.sleep(0.5)
    
def readAmbientSensor():
    humidity = -1
    ambtemp = -1
    try:
        # this seems to retry enough on its own that
        # I don't need my own process around that
        humidity, ambtemp = Adafruit_DHT.read_retry(sensor, gpio_pin)
        
        # Its either None or a Celsius temp
        if ambtemp is not None and ambtemp > -1:
            ambtemp = (ambtemp*(9/5))+32
        else :
            ambtemp = -1
            humidity = -1
    except:
        humidity = -1
        ambtemp = -1
        print("Error getting ambient sensor info at " + datetime.datetime.now().isoformat())
    
    return humidity, ambtemp
    
def aggregateFermDPs(fermdp):
    dpList.append(copy(fermdp))
    time_diff = (fermdp.getTimestamp() - dpList[0].getTimestamp()).seconds
    print("Time diff: " + str(time_diff))
    #Enough time has passed, aggregate all the datapoints and record it
    if time_diff > 20: #Update this for real value aggregation
        gravity = 0
        fTemp = 0
        aTemp = 0
        humidity = 0
        for dp in dpList:
            gravity += dp.getGravity()
            fTemp += dp.getFermTemp()
            aTemp += dp.getAmbTemp()
            humidity += dp.getHumidity()
        gravity = gravity / len(dpList)
        fTemp = fTemp / len(dpList)
        aTemp = aTemp / len(dpList)
        humidity = humidity / len(dpList)
        print("Aggregated Data Point...")
        print("T = " + str(fermdp.getTimestamp()))
        print("G = " + "{:4.3f}".format(gravity))
        print("F = " + "{:3.1f}".format(fTemp))
        print("A = " + "{:3.1f}".format(aTemp))
        senddata = {
            'Time': fermdp.getTimestamp(),
            'SG': "{:4.3f}".format(gravity),
            'Temp': "{:3.1f}".format(fTemp),
            'Color': "Purple",
            'Beer': CURRENT_BEER_NAME,
            'Comment': "{:3.1f}".format(aTemp)
            }
        r = requests.post(SHEETS_SCRIPT, senddata)
        print(r) #???
        dpList.clear()
        dpList.clear()
    
def monitor_tilt():
    #sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    # default printing values of -1
    fermdp = fermdatapoint.FermPoint()
    # We're just sharing a single object...obviously this will have to change
    screenThread = threading.Thread(target=ScreenLoop, args=(fermdp,))
    screenThread.start()
    #with sender:
    while True:
        # this parameter is 100 "scans", however it returns the first
        # valid uuid (color) that it finds, which is usually VERY quick
        beacons = blescan.parse_events(sock, 100)
        for beacon in beacons:
            #get ambient
            humidity, ambtemp = readAmbientSensor()
            fermdp.updateFermPoint(beacon['color'], beacon['temp'], ambtemp, beacon['grav'], humidity, datetime.datetime.now())
            #publish
            #print(fermdp.toJSON())
            aggregateFermDPs(fermdp)
            #sender.send_messages(ServiceBusMessage(fermdp.toJSON()))
        time.sleep(2) #for now just get an update every ~5s

if __name__ == '__main__':
    dev_id = 0
    try:
        sock = bluez.hci_open_dev(dev_id)
        print('Starting Fermentation Tracking...')
    except:
        print('Error accessing bluetooth device...')
        sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)
    #servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
    #with servicebus_client: #tab the monitor_tilt if using sb
    monitor_tilt()
    
