#!/usr/bin/python
import sys
import RPi.GPIO as GPIO
import time
import os
import paho.mqtt.client as mqtt

server_ip = sys.argv[1]
room_id = sys.argv[2]
sensor_id = sys.argv[3]
sensor_pin = int(sys.argv[4])

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, GPIO.PUD_DOWN)

client = mqtt.Client()
client.connect(server_ip, 1883, 60)
previous_soil_humidity = False
current_soil_humidity = False

while True:
  time.sleep(0.3)
  previous_soil_humidity = current_soil_humidity
  current_soil_humidity = GPIO.input(sensor_pin)
  if current_soil_humidity != previous_soil_humidity:
      if current_soil_humidity == False:
          print("SOIL HUMIDITY DETECTED! (Room " + room_id + " - Soil humidity sensor " + sensor_id + ")")
	  message = "rooms/" + room_id + "/soil_humidity_sensors/" + sensor_id + "/1"
	  print(message)
 	  client.publish("soil_humidity_sensors", message)
      else:
	  print("... (Room " + room_id + " - Soil humidity sensor " + sensor_id + ")")
	  message = "rooms/" + room_id + "/soil_humidity_sensors/" + sensor_id + "/0"
          print(message)
          client.publish("soil_humidity_sensors", message)
