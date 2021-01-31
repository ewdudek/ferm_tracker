# TODO UPDATE REFERENCES/SOURCES
# Ambient sensor: https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/

#make obj out of datapoint
#send to azure sb sender
#https://blog.softhints.com/python-convert-object-to-json-3-examples/#built
#add timing based around looking for data
#add retries around getting tilt data

#this loop is garbage.
#try threading? https://realpython.com/intro-to-python-threading/

import sys
import datetime
import time
import subprocess
import bluetooth._bluetooth as bluez
import blescan
import Adafruit_DHT
import adascreen

# DHT Sensor Type
sensor = Adafruit_DHT.AM2302
gpio_pin = 4 #Should I move the pin?

def distinct(objects):
    seen = set()
    unique = []
    for obj in objects:
        if obj['uuid'] not in seen:
            unique.append(obj)
            seen.add(obj['uuid'])
    return unique
    
def readAmbientSensor():
    humidity = -1
    ambtemp = -1
    try:
        humidity, ambtemp = Adafruit_DHT.read_retry(sensor, gpio_pin)
        if ambtemp is None:
            print("First temp probe failed, wait 2s then try again...")
            #sensor has weird issues with checking the temp within 2s, so do max delay
            time.sleep(2)
            humidity, ambtemp = Adafruit_DHT.read_retry(sensor, gpio_pin)
            if ambtemp is None:
                ambtemp = -1
                humidity = -1
        
        if ambtemp is not None and ambtemp > -1:
            ambtemp = (ambtemp*(9/5))+32
    except:
        humidity = -1
        ambtemp = -1
        print("Error getting ambient sensor info at " + datetime.datetime.now().isoformat())
    
    return humidity, ambtemp
    
def monitor_tilt():
    #default printing values
    color = 'unknown'
    timestamp = datetime.datetime.now()
    prev_timestamp = timestamp
    update_diff = -1
    gravity = -1
    fermtemp = -1
    ambtemp = -1
    humidity = -1
    adascreen.drawDataPoint(color, gravity, fermtemp, ambtemp, update_diff)
    while True:
        #do 10 loops of bluetooth scanning
        beacons = distinct(blescan.parse_events(sock, 10))
        print(len(beacons))
        for beacon in beacons:
            #get ambient
            humidity, ambtemp = readAmbientSensor()
            
            timestamp = datetime.datetime.now()
            update_diff = (timestamp - prev_timestamp).seconds
            fermtemp = beacon['major']
            gravity = beacon['minor']/1000
            #update display
            adascreen.drawDataPoint(color, gravity, fermtemp, ambtemp, update_diff)
            prev_timestamp = timestamp
                
        time.sleep(8)

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
    monitor_tilt()
    
