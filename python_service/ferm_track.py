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
import bluetooth._bluetooth as bluez
import blescan
import Adafruit_DHT
import adascreen

# DHT Sensor Type
sensor = Adafruit_DHT.AM2302 # Same as DHT22, no?
gpio_pin = 26 # I think this is GPIO pin not literal pin #

# I feel like I just wrote a java class in python
class FermPoint:
    def __init__(self):
        self.fermTemp = -1
        self.ambTemp = -1
        self.color = "Unknown"
        self.gravity = -1
        self.humidity = -1
        self.timestamp = datetime.datetime.now()
        self._lock = threading.Lock()
    
    def updateFermPoint(self, newColor, newFermTemp, newAmbTemp, newGravity, newHumidity, newTimestamp):
        with self._lock:
            self.color = newColor
            self.fermTemp = newFermTemp
            self.ambTemp = newAmbTemp
            self.gravity = newGravity
            self.humidity = newHumidity
            self.timestamp = newTimestamp
    
    def getColor(self):
        return self.color
    def getFermTemp(self):
        return self.fermTemp
    def getAmbTemp(self):
        return self.ambTemp
    def getGravity(self):
        return self.gravity
    def getHumidity(self):
        return self.humidity
    def getTimestamp(self):
        return self.timestamp

def ScreenLoop(fermdp):
    while True:
        update_diff = (datetime.datetime.now() - fermdp.getTimestamp()).seconds
        adascreen.drawDataPoint(fermdp.getColor(), fermdp.getGravity(), fermdp.getFermTemp(), fermdp.getAmbTemp(), update_diff)
        time.sleep(0.25)
    
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
    except:
        humidity = -1
        ambtemp = -1
        print("Error getting ambient sensor info at " + datetime.datetime.now().isoformat())
    
    return humidity, ambtemp
    
def monitor_tilt():
    # default printing values of -1
    fermdp = FermPoint()
    # We're just sharing a single object...obviously this will have to change
    screenThread = threading.Thread(target=ScreenLoop, args=(fermdp,))
    screenThread.start()
    i=1
    while True:
        # this parameter is 100 "scans", however it returns the first
        # valid uuid (color) that it finds, which is usually VERY quick
        beacons = blescan.parse_events(sock, 100)
        for beacon in beacons:
            #get ambient
            #humidity, ambtemp = readAmbientSensor()
            fermdp.updateFermPoint(beacon['color'], beacon['temp'], -1, beacon['grav'], -1, datetime.datetime.now())
            #publish
        
        time.sleep(5) #for now just get an update every ~5s

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
    
