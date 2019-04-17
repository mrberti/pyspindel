"""
This script will be run as soon as the ESP8266 device starts. All major
hardware initilizations should be done here.
"""
try:
    import time
except ImportError:
    import utime as time

# Hardware specific defines
import machine
import wemos

# Initialize Pins
SCL = machine.Pin(wemos.SCL)
SDA = machine.Pin(wemos.SDA)
LED = wemos.LED()

# Initialize I2C
I2C = machine.I2C(scl=SCL, sda=SDA, freq=400000)

# The acces point interface should be disabled (for future implementation of
# multicast)
wemos.AP_IF.active(False)
# Initialize wifi
WIFI = wemos.STA_IF
WIFI.active(True)
# The Wifi should be connected
for i in range(100):
    if WIFI.isconnected():
        break
    time.sleep_ms(250)
    LED.toggle()
else:
    LED.off()
    raise Exception("Could not connect to Wifi")
print("Connected to Wifi '{}': {}, {} dB"
      .format(WIFI.config("essid"), WIFI.ifconfig(), WIFI.status("rssi")))

# Indicate activity with LEDs
LED.on()

import stomp
stomp.main()

LED.off()
# wemos.go_to_sleep(1000)
