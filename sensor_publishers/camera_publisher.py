#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import sys
import paho.mqtt.client as mqtt

server_ip = sys.argv[1]
room_id = sys.argv[2]
camera_id = sys.argv[3]
camera_ip = sys.argv[4]
camera_port = sys.argv[5]

client = mqtt.Client()
client.connect(server_ip, 1883, 60)

print(camera_ip + ":" + camera_port + " (Room " + room_id + " - Camera " + camera_id + ")")
message = "rooms/" + room_id + "/cameras/" + camera_id + "/" + camera_ip + "/" + camera_port
print(message)
client.publish("cameras", message)

