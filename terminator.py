#!/usr/bin/python
import os

for pid in os.popen("ps aux | grep rpi_client | awk {'print $2'} | head -n -1").read().splitlines():
   os.system("sudo kill -9 %s" % pid)

for pid in os.popen("ps aux | grep sensor_publisher | awk {'print $2'} | head -n -1").read().splitlines():
   os.system("sudo kill -9 %s" % pid)

os.system("sudo python reset_gpios.py")
