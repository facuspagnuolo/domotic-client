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
previous_humidity = 0
current_humidity = 0

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Function to read SPI data from MCP3008 chip
def read_channel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

while True:
  time.sleep(5)
  previous_humidity = current_humidity
  current_humidity = read_channel(sensor_mcp3008_channel)
  if current_humidity != previous_humidity:
    print "------------------------------------------------------"
    print "SOIL HUMIDITY:"
    message = "rooms/" + room_id + "/soil_humidity_sensors/" + sensor_id + "/" + str(current_humidity)
    print(message)
    client.publish("soil_humidity_sensors", message)
    print "------------------------------------------------------"
