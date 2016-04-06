#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import sys
import Adafruit_DHT
import paho.mqtt.client as mqtt

GPIO.setmode(GPIO.BCM)

serverIP = "192.168.0.10"

# GPIO sensors
ROOM_ID = "1"
LIGHTS = {"1":2, "2":3, "3":4, "4":17, "5":27, "6":22, "7":10, "8":9} 
TEMPERATURE_SENSORS = {"1":21} 
HUMIDITY_SENSOR ={"1":21}
MOTION_SENSOR_PIN = 11
MOTION_SENSOR_ID = 1

# loop through pins and set mode and state to 'low'
GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN, GPIO.PUD_DOWN)
for key in LIGHTS: 
    GPIO.setup(LIGHTS[key], GPIO.OUT) 
    GPIO.output(LIGHTS[key], GPIO.HIGH)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe("rooms/"+ROOM_ID)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    request = str(msg.payload)
    type = request.split('/')[0]
    id = request.split('/')[1]
    
    if type == 'lights':
	if GPIO.input(LIGHTS[id]) == True:
            print("Switching ON light ("+id+")")
            GPIO.output(LIGHTS[id], GPIO.LOW)
            client.publish("lights", "rooms/"+ROOM_ID+"/lights/"+id+"/ON")
        else:
            print("Switching OFF light ("+id+")")
            GPIO.output(LIGHTS[id], GPIO.HIGH)
            client.publish("lights", "rooms/"+ROOM_ID+"/lights/"+id+"/OFF")

    if type == 'tvs':
	if request.split('/')[2] == 'ON':
            print("Turning ON tv ("+id+")")
            os.system('echo "on '+id+'" | cec-client -s')
            client.publish("tvs", "rooms/"+ROOM_ID+"/tvs/"+id+"/ON")
        else:
            print("Turning OFF tv ("+id+")")
            os.system('echo "standby '+id+'" | cec-client -s')
            client.publish("tvs", "rooms/"+ROOM_ID+"/tvs/"+id+"/OFF")

    if type == 'temperature_sensors':
        humidity, temperature = Adafruit_DHT.read_retry(HUMIDITY_SENSORS[id], TEMPERATURE_SENSORS[id])
        if temperature is not None:
	    print 'Temperature ('+id+') = {0:0.1f}*C'.format(temperature)
	    client.publish("temperature_sensors", "rooms/"+ROOM_ID+"/temperature_sensors/"+id+"/"+str('{0:0.1f}'.format(temperature)))
        else:
            print 'Failed to sense temperature!'
	    client.publish("temperature_sensors", "rooms/"+ROOM_ID+"/temperature_sensors/"+id+"/failed")

    if type == 'humidity_sensors':
        humidity, temperature = Adafruit_DHT.read_retry(HUMIDITY_SENSOR[id], TEMPERATURE_SENSOR[id])
        if humidity is not None:
	    print 'Humidity ('+id+') = {0:0.1f}%'.format(humidity)
	    client.publish("humidity_sensors", "rooms/"+ROOM_ID+"/humidity_sensors/"+id+"/"+str('{0:0.1f}'.format(humidity)))
        else:
            print 'Failed to sense humidity!'
	    client.publish("humidity_sensors", "rooms/"+ROOM_ID+"/humidity_sensors/"+id+"/failed")



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(serverIP, 1883, 60)

# Alarm
previous_state = False
current_state = False
while True:
    previous_state = current_state
    current_state = GPIO.input(MOTION_SENSOR_PIN)
    if current_state != previous_state:
        if current_state == True:
	    print("MOTION DETECTED!")
	    client.publish("motion_sensors", str(MOTION_SENSOR_ID)+"/ON")
	else:
	    print("...")
            client.publish("motion_sensors", str(MOTION_SENSOR_ID)+"/OFF")
    client.loop()
