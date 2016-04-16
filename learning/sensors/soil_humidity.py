#!/usr/bin/python
import RPi.GPIO as GPIO
import time

sensor_pin = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, GPIO.PUD_DOWN)

while True:
  soil_humidity = GPIO.input(sensor_pin)
  print("Soil humidity: {0:0.1f}".format(soil_humidity))
  time.sleep(1)
