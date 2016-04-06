#!/usr/bin/python

import spidev
import time
import os

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

config_id = 0x14;
quad_set = 0x01;
resp = spi.xfer2([config_id])
print resp
time.sleep(5)
resp = spi.xfer2([quad_set])
print resp
