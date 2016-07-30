#!/usr/bin/python
import paho.mqtt.client as mqtt
import spidev
import time
import sys
import os

server_ip = sys.argv[1]
room_id = sys.argv[2]
sensor_id = sys.argv[3]
sensor_mcp3008_channel = int(sys.argv[4])

client = mqtt.Client()
client.connect(server_ip, 1883, 60)
previous_luminosity = 0
current_luminosity = 0

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Function to read SPI data from MCP3008 chip
def read_channel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

while True:
  time.sleep(2)
  previous_luminosity = current_luminosity
  current_luminosity = read_channel(sensor_mcp3008_channel)
  if current_luminosity != previous_luminosity:
    print "------------------------------------------------------"
    print "LUMINOSITY:"
    message = "rooms/" + room_id + "/luminosity_sensors/" + sensor_id + "/" + str(current_luminosity)
    print(message)
    client.publish("luminosity_sensors", message)
    print "------------------------------------------------------"
