# TODO UPDATE REFERENCES/SOURCES
# Ambient sensor: https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/

#make obj out of datapoint
#send to azure sb sender
#https://blog.softhints.com/python-convert-object-to-json-3-examples/#built
#add timing based around looking for data
#add retries around getting tilt data

import sys
import datetime
import time
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import bluetooth._bluetooth as bluez
import blescan
import Adafruit_DHT

TILTS = {
		'a495bb40c5b14b44b5121370f02d74de': 'Purple',
        'a495bb10c5b14b44b5121370f02d74de': 'Red',
        'a495bb20c5b14b44b5121370f02d74de': 'Green',
        'a495bb30c5b14b44b5121370f02d74de': 'Black',
        'a495bb50c5b14b44b5121370f02d74de': 'Orange',
        'a495bb60c5b14b44b5121370f02d74de': 'Blue',
        'a495bb70c5b14b44b5121370f02d74de': 'Yellow',
        'a495bb80c5b14b44b5121370f02d74de': 'Pink',
}

#Adafruit OLED Screen Stuff:
# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
# Create the SSD1306 OLED class with pixel h&w
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
# Clear display.
disp.fill(0)
disp.show()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
# Load default font.
font = ImageFont.load_default()
# DHT Sensor Type
sensor = Adafruit_DHT.AM2302
gpio_pin = 4 #Should I move the pin?

def drawDataPoint(color, gravity, fermtemp, ambtemp, timediff):
    try:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x, top + 0), "Gravity: " + "{:4.3f}".format(gravity), font=font, fill=255)
        draw.text((x, top + 8), "Ferm Temp: " + "{:3.1f}".format(fermtemp) + "F", font=font, fill=255)
        draw.text((x, top + 16), "Amb Temp: " + "{:3.1f}".format(ambtemp) + "F", font=font, fill=255)
        draw.text((x, top + 25), "Last Update: " + str(timediff) + "s", font=font, fill=255)
        # Display image.
        disp.image(image)
        disp.show()
        time.sleep(0.1)
    except:
        print("Failed to update LCD at " + datetime.datetime.now().isoformat())

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
        #get ambient
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
    drawDataPoint(color, gravity, fermtemp, ambtemp, update_diff)
    while True:
        humidity, ambtemp = readAmbientSensor()
        print("Ambient Temp: " + str(ambtemp) + " Humidity: " + str(humidity))
        timestamp = datetime.datetime.now()
        print("Timestamp: " + str(timestamp))
        update_diff = (timestamp - prev_timestamp).seconds
        print("Time Diff? " + str(update_diff))
        #update display
        drawDataPoint(color, gravity, fermtemp, ambtemp, update_diff)
        prev_timestamp = timestamp
        time.sleep(10)

if __name__ == '__main__':
    dev_id = 0
    try:
        print('Starting Fermentation Tracking...')
    except:
        print('Error accessing bluetooth device...')
        sys.exit(1)

    monitor_tilt()
    
