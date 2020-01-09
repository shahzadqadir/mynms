#!/usr/bin/python3
from easysnmp import Session
import os

class GetSNMP:

    def get_hostname(ip_add, snmp_community):
        try:        
            session = Session(hostname=ip_add, community=snmp_community, version=2)
        except SystemError:
            print("host unreachable")                        
        hostname = session.get('iso.3.6.1.2.1.1.5.0')
        return hostname.value

    def get_version(ip_add, snmp_community):
        session = Session(hostname=ip_add, community=snmp_community, version=2)
        version = session.get('iso.3.6.1.2.1.1.1.0')
        return version.value

    def get_serial_no(ip_add, snmp_community):
        session = Session(hostname=ip_add, community=snmp_community, version=2)
        serial_no = session.get('iso.3.6.1.2.1.47.1.1.1.1.11.1')
        return serial_no.value



