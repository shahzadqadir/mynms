#!/usr/bin/python3

from platform import platform
from os import system

class Connectivity:
    
    def check_connectivity(self, host):
        if "inux" in platform():
            return self.host_chk_linux(host)
        elif "indow" in platform():
            return self.host_chk_win(host)            
    
    def host_chk_win(self, host):
        if system(f"ping -n 3 -w 999 {host} > null") == 0:
            return True
        return False
    
    def host_chk_linux(self, host):
        if system(f"ping -c 3 -W 2 {host} >> /dev/null") == 0:
            return True
        return False

        


