#!/usr/bin/python
from constants import *
import socket
import os

network = ''
password = ''

def get_network_data():
   global network
   global password

   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
   os.system('echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" > wpa_supplicant.conf')
   os.system('echo "update_config=1" >> wpa_supplicant.conf')
   os.system('echo "" >> wpa_supplicant.conf')
   os.system('echo "network={" >> wpa_supplicant.conf')
   os.system("""echo '     ssid=\"%s\"' >> wpa_supplicant.conf""" % network)
   os.system("""echo '     psk=\"%s\"' >> wpa_supplicant.conf""" % password)
   os.system('echo "}" >> wpa_supplicant.conf')

def connect_to_network():
  os.system('sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')
  os.system('sudo cp /etc/network/interfaces_default /etc/network/interfaces')
  os.system('sudo ifdown wlan0')
  os.system('sudo ifup wlan0')

get_network_data()
build_network_configuration_file()
connect_to_network()
