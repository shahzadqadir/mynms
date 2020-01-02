#!/usr/bin/python3
import telnetlib

tn = telnetlib.Telnet("192.168.0.4", 23)
#tn.read_until("login:")
print(tn)