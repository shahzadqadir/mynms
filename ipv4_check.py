#!/usr/bin/python3
import re

class IPv4Check:

    def check_ip_format(ip_address):
        ip_format = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\/(\d{1,2})$")
        result = ip_format.search(ip_address)
        if result:
            return True
        return False

    def check_file_format(filename):
        csv_format = re.compile(r"[a-zA-Z0-9].csv$")
        txt_format = re.compile(r"[a-zA-Z0-9].txt")
        if csv_format.search(filename) or txt_format.search(filename):
            return True
        return False

    def check_file_type(filename):
        csv_format = re.compile(r"[a-zA-Z0-9].csv$")
        txt_format = re.compile(r"[a-zA-Z0-9].txt")
        if csv_format.search(filename):
            return ".csv"
        elif txt_format.search(filename):
            return ".txt"

    def check_valid_ip(ip_string):
        ip_4_octet = ip_string.split('/')
        ip_list = ip_4_octet[0].split(".")
        if int(ip_list[0]) < 1 or int(ip_list[0]) > 255:
            return False
        if int(ip_list[3]) < 0 or int(ip_list[3]) > 254:
            return False
        if int(ip_list[1]) < 0 or int(ip_list[1]) > 255:
            return False
        if int(ip_list[2]) < 0 or int(ip_list[2]) > 255:
            return False
        return True

#print(IPv4Check.check_file_format("123test.txt"))
