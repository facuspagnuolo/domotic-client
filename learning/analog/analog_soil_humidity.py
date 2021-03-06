#!/usr/bin/python
import spidev
import time
import os
 
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Define constants
channel = 5
delay = 2

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
 
# Function to convert data to voltage level, rounded to specified number of decimal places.
def ConvertVolts(data, places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts, places)
  return volts
 
# Function to calculate humidity, rounded to specified number of decimal places.
def ConvertHumidity(volts, places):
  humidity = (volts - 3.3) / float(-2.3 / float(950))
  humidity = round(humidity, places)
  return humidity
 
while True:
  channel_input = ReadChannel(channel)
  volts = ConvertVolts(channel_input, 2)
  humidity = ConvertHumidity(volts, 2)
  print "--------------------------------------------"
  print("Humidity: {} ({}V)".format(humidity, volts))
  time.sleep(delay)
