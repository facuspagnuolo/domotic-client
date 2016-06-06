#!/usr/bin/python
import paho.mqtt.client as mqtt
import spidev
import time
import sys
import os

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

server_ip = sys.argv[1]
room_id = sys.argv[2]
sensor_id = sys.argv[3]
sensor_mcp3008_channel = int(sys.argv[4])

client = mqtt.Client()
client.connect(server_ip, 1883, 60)
previous_humidity = 0
current_humidity = 0

# Function to read SPI data from MCP3008 chip
def read_channel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

# Function to convert data to voltage level, rounded to specified number of decimal places.
def convert_volts(data, places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts, places)
  return volts

# Function to calculate humidity, rounded to specified number of decimal places.
def convert_humidity(volts, places):
  humidity = (volts - 3.3) / float(-2.3 / float(950))
  humidity = round(humidity, places)
  return humidity

while True:
  previous_humidity = current_humidity
  channel_input = read_channel(sensor_mcp3008_channel)
  volts = convert_volts(channel_input, 2)
  current_humidity = convert_humidity(volts, 2)
  if current_humidity != previous_humidity:
    print "------------------------------------------------------"
    print "SOIL HUMIDITY:"
    message = "rooms/" + room_id + "/soil_humidity_sensors/" + sensor_id + "/" + str(current_humidity)
    print(message)
    client.publish("soil_humidity_sensors", message)
    print "------------------------------------------------------"
  time.sleep(2)
