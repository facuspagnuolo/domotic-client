#!/usr/bin/python
from constants import *
import RPi.GPIO as GPIO
import os
import subprocess
import sys
import paho.mqtt.client as mqtt
import socket
import struct
import time

GPIO.setmode(GPIO.BCM)
domotic_server_ip = ''
network = ''
password = ''

def initialize_gpios():
   GPIO.setmode(GPIO.BCM)
   for key in LIGHT_PINS:
      GPIO.setup(LIGHT_PINS[key], GPIO.OUT)
      GPIO.output(LIGHT_PINS[key], GPIO.HIGH)
   for key in VALVE_PINS:
      GPIO.setup(VALVE_PINS[key], GPIO.OUT)
      GPIO.output(VALVE_PINS[key], GPIO.HIGH)
    
def get_network_data():
   global network
   global password

   print "Waiting for adhoc connection from the server"
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   sock.bind((NETWORK_DISCOVERY_SERVER_IP, NETWORK_DISCOVERY_SERVER_PORT))
   sock.listen(1)
   session, client_address = sock.accept()
   print 'Got connection from ', client_address

   while (network == '') and (password == ''):
      network_data = session.recv(1024)
      network_data = network_data.split('|')
      network = network_data[0]
      password = network_data[1]

   session.send("Connecting to network %s with password %s" %(network, password))
   session.close

def build_network_configuration_file():
   os.system('echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" > config/wpa_supplicant.conf')
   os.system('echo "update_config=1" >> config/wpa_supplicant.conf')
   os.system('echo "" >> config/wpa_supplicant.conf')
   os.system('echo "network={" >> config/wpa_supplicant.conf')
   os.system("""echo '     ssid=\"%s\"' >> config/wpa_supplicant.conf""" % network)
   os.system("""echo '     psk=\"%s\"' >> config/wpa_supplicant.conf""" % password)
   os.system('echo "}" >> config/wpa_supplicant.conf')

def restart_ad_hoc():
   print 'Restarting DHCP adhoc server'
   os.system('sudo service isc-dhcp-server restart')
   print 'Restarting adhoc interface'
   os.system('sudo ifdown wlan1')
   os.system('sudo ifup wlan1')

def connect_to_network():
   print "Connecting to network %s with password %s" %(network, password)
   os.system('sudo cp config/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')
   os.system('sudo ifdown wlan0')
   os.system('sudo ifup wlan0')

def find_and_connect_to_network():
   restart_ad_hoc()
   get_network_data()
   build_network_configuration_file()
   connect_to_network()

def get_domotic_server_ip():
   global domotic_server_ip
   while True:
      print "Traying to open to multicast server"
      try:
  	 sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	 sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	 sock.bind((PING_SERVER_MULTICAST_IP, PING_SERVER_MULTICAST_PORT))
	 mreq = struct.pack("4sl", socket.inet_aton(PING_SERVER_MULTICAST_IP), socket.INADDR_ANY)
	 sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	 print 'Waiting for domotic server to start'
	 data, addr = sock.recvfrom(1024)
	 domotic_server_ip = str(addr[0])
	 print '%s from %s' % (data, domotic_server_ip)
	 break
      except Exception, e:
         print "Could not reach domotic server :" + str(e)
	 time.sleep(2)
         continue

def initialize_publishers():
   print("Initialize cameras publishers")
   for key in CAMERAS:
      pid = subprocess.Popen(["sudo", "python", "sensor_publishers/camera_publisher.py", domotic_server_ip, ROOM_ID, key, CAMERAS[key]]).pid
      os.system("echo '%s' > logs/subprocesses_pids.txt" % str(pid))

   print("Initialize motion sensors publishers")
   for key in MOTION_SENSOR_PINS:
      pid = subprocess.Popen(["sudo", "python", "sensor_publishers/motion_sensor_publisher.py", domotic_server_ip, ROOM_ID, key, str(MOTION_SENSOR_PINS[key])]).pid
      os.system("echo '%s' >> logs/subprocesses_pids.txt" % str(pid))

   print("Initialize temperature and humidity sensors publishers")
   for key in TEMPERATURE_SENSOR_PINS:
      pid = subprocess.Popen(["sudo", "python", "sensor_publishers/temperature_and_humidity_sensor_publisher.py", domotic_server_ip, ROOM_ID, key, str(TEMPERATURE_SENSOR_PINS[key])]).pid
      os.system("echo '%s' >> logs/subprocesses_pids.txt" % str(pid))

   print("Initialize luminosity sensors publishers")
   for key in LUMINOSITY_SENSOR_PINS:
      pid = subprocess.Popen(["sudo", "python", "sensor_publishers/luminosity_analog_sensor_publisher.py", domotic_server_ip, ROOM_ID, key, str(LUMINOSITY_SENSOR_MCP3008_CHANNELS[key])]).pid
      os.system("echo '%s' >> logs/subprocesses_pids.txt" % str(pid))

   print("Initialize soil humidity sensors publishers")
   for key in SOIL_HUMIDITY_SENSOR_PINS:
      pid = subprocess.Popen(["sudo", "python", "sensor_publishers/soil_humidity_analog_sensor_publisher.py", domotic_server_ip, ROOM_ID, key, str(SOIL_HUMIDITY_SENSOR_MCP3008_CHANNELS[key])]).pid
      os.system("echo '%s' >> logs/subprocesses_pids.txt" % str(pid))

def on_connect(client, userdata, rc):
   client.subscribe("rooms/" + ROOM_ID)
   print("RPI room client connected with result code "+str(rc))

def on_message(client, userdata, msg):
   request = str(msg.payload)
   type = request.split('/')[0]
   id = request.split('/')[1]
   action = request.split('/')[2]

   if type == 'lights':
      if action == 'ON':
         print("Switching ON light ("+id+")")
         GPIO.output(LIGHT_PINS[id], GPIO.LOW)
         client.publish("lights", "rooms/"+ ROOM_ID +"/lights/"+id+"/ON")
      if action == 'OFF':
         print("Switching OFF light ("+id+")")
         GPIO.output(LIGHT_PINS[id], GPIO.HIGH)
         client.publish("lights", "rooms/"+ ROOM_ID +"/lights/"+id+"/OFF")
    
   if type == 'tvs':
      if action == 'ON':
         print("Turning ON tv ("+id+")")
         os.system('echo "on '+id+'" | cec-client -s')
         client.publish("tvs", "rooms/"+ ROOM_ID +"/tvs/"+id+"/ON")
      if action == 'OFF':
         print("Turning OFF tv ("+id+")")
         os.system('echo "standby '+id+'" | cec-client -s')
         client.publish("tvs", "rooms/"+ ROOM_ID +"/tvs/"+id+"/OFF")

   if type == 'valves':
      if action == 'ON':
         print("Opening valve ("+id+")")
         GPIO.output(VALVE_PINS[id], GPIO.LOW)
         client.publish("valves", "rooms/"+ ROOM_ID +"/valves/"+id+"/ON")
      if action == 'OFF':
         print("Closing valve ("+id+")")
         GPIO.output(VALVE_PINS[id], GPIO.HIGH)
         client.publish("valves", "rooms/"+ ROOM_ID +"/valves/"+id+"/OFF")


find_and_connect_to_network()
get_domotic_server_ip()
initialize_gpios()
initialize_publishers()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(domotic_server_ip, 1883, 60)
client.loop_forever()
