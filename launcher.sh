#!/bin/sh

cd /home/pi/Desktop/domotic-client
sudo stdbuf -oL python rpi_client.py > logs/rpi_client.log
