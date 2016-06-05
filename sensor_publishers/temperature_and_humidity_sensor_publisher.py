#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import sys
import Adafruit_DHT
import paho.mqtt.client as mqtt

server_ip = sys.argv[1]
room_id = sys.argv[2]
sensor_id = sys.argv[3]
sensor_pin = int(sys.argv[4])

client = mqtt.Client()
client.connect(server_ip, 1883, 60)
previous_temperature = 0
previous_humidity = 0
current_temperature = 0
current_humidity = 0

while True:
  time.sleep(5)
  previous_temperature = current_temperature
  previous_humidity = current_humidity
  current_humidity, current_temperature = Adafruit_DHT.read_retry(sensor_pin, sensor_pin)
  
  if current_temperature != previous_temperature:
      print "------------------------------------------------------"
      if current_temperature is not None:
          print "TEMPERATURE:"
	  message = "rooms/" + room_id + "/temperature_sensors/" + sensor_id + "/" + str('{0:0.1f}'.format(current_temperature))
	  print(message)
          client.publish("temperature_sensors", message)
      else:
          print "TEMPERATURE (failed):"
	  message = "rooms/" + room_id + "/temperature_sensors/" + sensor_id + "/failed"
	  print(message)
          client.publish("temperature_sensors", message)
      print "------------------------------------------------------"
  
  if current_humidity != previous_humidity:
      print "------------------------------------------------------"
      if current_humidity is not None:
          print "HUMIDITY:"
	  message = "rooms/" + room_id + "/humidity_sensors/" + sensor_id + "/" + str("{0:0.1f}".format(current_humidity))
	  print(message)
          client.publish("humidity_sensors", message)
      else:
          print "HUMIDITY (failed):"
	  message = "rooms/" + room_id + "/humidity_sensors/" + sensor_id + "/failed"
	  print(message)
	  client.publish("humidity_sensors", message)
      print "------------------------------------------------------"
