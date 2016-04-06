#!/usr/bin/python
from constants import *
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

for key in LIGHT_PINS:
    GPIO.setup(LIGHT_PINS[key], GPIO.OUT)
    GPIO.output(LIGHT_PINS[key], GPIO.HIGH)

for key in VALVE_PINS:
    GPIO.setup(VALVE_PINS[key], GPIO.OUT)
    GPIO.output(VALVE_PINS[key], GPIO.HIGH)

GPIO.cleanup()
