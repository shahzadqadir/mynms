#!/usr/bin/python3

import paramiko

def show_cmd(hostname, username, password, command):
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn.connect(hostname=hostname, username=username, password=password)
    stdin, stdout, stderr = conn.exec_command(command)
    stdout = stdout.readlines()
    return stdout




 

