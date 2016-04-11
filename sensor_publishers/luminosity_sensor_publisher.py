#!/usr/bin/python
import sys
import RPi.GPIO as GPIO
import time
import os
import Adafruit_DHT
import paho.mqtt.client as mqtt

GPIO.setmode(GPIO.BCM)
server_ip = sys.argv[1]
room_id = sys.argv[2]
sensor_id = sys.argv[3]
sensor_pin = int(sys.argv[4])
GPIO.setup(sensor_pin, GPIO.IN, GPIO.PUD_DOWN)

client = mqtt.Client()
client.connect(server_ip, 1883, 60)
previous_state = True
current_state = True

while True:
  time.sleep(0.3)
  previous_state = current_state
  current_state = GPIO.input(sensor_pin)
  if current_state != previous_state:
      if current_state == False:
          print("LIGHT DETECTED! (Room " + room_id + " - Luminosity sensor " + sensor_id + ")")
	  message = "rooms/" + room_id + "/luminosity_sensors/" + sensor_id + "/1"
	  print(message)
          client.publish("luminosity_sensors", message)
      else:
          print("... (Room " + room_id + " - Luminosity sensor " + sensor_id + ")")
	  message = "rooms/" + room_id + "/luminosity_sensors/" + sensor_id + "/0"          
          print(message)
          client.publish("luminosity_sensors", message)

