from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

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
        #time.sleep(0.1)
    except:
        print("Failed to update LCD at " + datetime.datetime.now().isoformat())
