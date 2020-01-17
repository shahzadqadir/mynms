#!/usr/bin/python3

import paramiko
import telnetlib
import time
#from builtins import True

def connection_test_ssh(hostname, username, password):
    try:        
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(hostname=hostname, username=username, password=password, allow_agent=False,look_for_keys=False)
        stdin, stdout, stderr = conn.exec_command("show version")
        stdout = stdout.readlines()
        return True
    except paramiko.ssh_exception.AuthenticationException:
        return False
    except paramiko.ssh_exception.NoValidConnectionsError:
        return False

def show_cmd_ssh(hostname, username, password, command):        
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn.connect(hostname=hostname, username=username, password=password, allow_agent=False,look_for_keys=False)
    stdin, stdout, stderr = conn.exec_command(command)
    stdout = stdout.readlines()
    return stdout

def config_cmd_ssh(hostname, username, password, cmd_list):
    try:
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(hostname=hostname, username=username, password=password, allow_agent=False,look_for_keys=False)
    except paramiko.ssh_exception.AuthenticationException:
        return False
    except paramiko.ssh_exception.NoValidConnectionsError:
        return False
    
    rtcon = conn.invoke_shell()
    time.sleep(1)
    
    for command in cmd_list:
        rtcon.send(command + '\n')
        time.sleep(1)
        
    return True


def show_telnet_cisco(host, username, password, command):
    tn = telnetlib.Telnet(host, timeout=3)
    tn.read_until(b"sername", 3)
    tn.write(username.encode('ascii') + b"\n")
    tn.read_until(b"assword", 3)
    tn.write(password.encode('ascii') + b"\n")
    tn.write(b"terminal length 0" + b"\n")
    tn.write(command.encode('ascii')+ b"\n")
    time.sleep(1)
    tn.write(b"exit" + b"\n")
    output = tn.read_all().decode().strip('\r').split('\n')
    tn.close()
    return output

def connection_test_telnet(host, username, password):
    try:
        tn = telnetlib.Telnet(host, timeout=3)
        tn.read_until(b"sername", 3)
        tn.write(username.encode('ascii') + b"\n")
        tn.read_until(b"assword", 3)
        tn.write(password.encode('ascii') + b"\n")
        tn.write(b"terminal length 0" + b"\n")
        tn.write(b"show version"+ b"\n")
        time.sleep(1)
        tn.write(b"exit" + b"\n")
        output = tn.read_all().decode().strip('\r').split('\n')
        tn.close()
        return True
    except:
        return False
    

def show_telnet_junos(host, username, password, command):
    
    tn = telnetlib.Telnet(host, timeout=3)
    
    try:
        tn.read_until(b"ogin:", 3)
        tn.write(username.encode('ascii') + b"\n")
        tn.read_until(b"assword:", 3)
        tn.write(password.encode('ascii') + b"\n")
    except:
        return "Invalid username or password"

    time.sleep(1)

    tn.write(b"set cli screen-length 0" + b"\n")
    tn.write(command.encode('ascii') + b"\n")
    
    # sleep before reading
    time.sleep(3)
    
    output = tn.read_very_eager().decode()
    tn.close()
    return output

# cmd_list = ["terminal length 0", "configure terminal", "interface ethernet1/1", "duplex full","switchport access vlan 10","end"]
# 
# if config_cmd_ssh("192.168.10.2", "nms", "cisco", cmd_list):
#     print("commands implmented successfully!")

# output = show_telnet_cisco("192.168.122.72", "nms", "cisco", "show version | in time")
# print(output[-3].strip('\n'))
# 
# print(output[-3].split(' ')[1])

#print(connection_test_telnet("192.168.122.77", "nms", "cisco"))

