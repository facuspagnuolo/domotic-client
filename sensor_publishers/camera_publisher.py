#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import sys
import paho.mqtt.client as mqtt

server_ip = sys.argv[1]
room_id = sys.argv[2]
camera_id = sys.argv[3]
camera_port = sys.argv[4]

client = mqtt.Client()
client.connect(server_ip, 1883, 60)

def get_ip_address():
    f = os.popen("ip a show wlan0 | grep 'inet ' | awk {'print $2'} | cut -f1 -d '/'")
    return f.read().rstrip('\n')

while True:
    camera_ip = get_ip_address()
    print(camera_ip + ":" + camera_port + " (Room " + room_id + " - Camera " + camera_id + ")")
    message = "rooms/" + room_id + "/cameras/" + camera_id + "/" + camera_ip + "/" + camera_port
    print(message)
    client.publish("cameras", message)
    time.sleep(10)
