#!/usr/bin/python
import sys
import RPi.GPIO as GPIO
import time
import os
import paho.mqtt.client as mqtt

GPIO.setmode(GPIO.BCM)
server_ip = sys.argv[1]
room_id = sys.argv[2]
sensor_id = sys.argv[3]
sensor_pin = int(sys.argv[4])
GPIO.setup(sensor_pin, GPIO.IN, GPIO.PUD_DOWN)

client = mqtt.Client()
client.connect(server_ip, 1883, 60)
previous_state = False
current_state = False

while True:
  previous_state = current_state
  current_state = GPIO.input(sensor_pin)
  if current_state != previous_state:
      print "------------------------------------------------------"
      if current_state == True:
          print "MOTION (detected):"  
	  message = "rooms/" + room_id + "/motion_sensors/" + sensor_id + "/ON"
  	  print(message)
          client.publish("motion_sensors", message)
      else:
          print "MOTION (not detected):"  
	  message = "rooms/" + room_id + "/motion_sensors/" + sensor_id + "/OFF"
	  print(message)
          client.publish("motion_sensors", message)
      print "------------------------------------------------------"
