#!/usr/bin/python
import os

pids = [line.rstrip('\n') for line in open('logs/subprocesses_pids.txt')]

for pid in pids:
   os.system("sudo kill -9 %s" % pid)

os.system("sudo python reset_gpios.py")
