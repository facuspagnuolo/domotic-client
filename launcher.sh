#!/bin/sh

cd /home/pi/Desktop/domotic-raspberry-client
sudo python reset_gpios.py 
sudo stdbuf -oL python rpi_client.py > logs/rpi_client.log
