#!/usr/bin/python3
# v2 adds Telnet and fixes some coding practice

import PyQt5
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox,\
    QTreeWidgetItem
from sys import argv
from PyQt5.Qt import QTableWidgetItem, QWidget
import MySQLdb
#### My imports
import cisco
from Connectivity import Connectivity
from GetSNMP import GetSNMP
from ipv4_check import IPv4Check
from ConfigInterface import L2IntfConfig

ui,_ = loadUiType('mynms_v3.ui')

class MainWindow(QMainWindow, ui):
    def __init__(self):
        self.ip = ""
        self.hostname = ""
        self.protocol = ""
        self.username = ""
        self.password = ""
        self.device_type = ""
        self.vendor = ""
        self.display_set = False
        self.connection_test = False
        #self.devices_info = {}     
        
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.populate_protocol_combo()
        self.populate_device_type_combo()
        self.button_handler()
        self.populate_commands_combo()
        self.populate_devices_tree()
        self.tree_devices.itemSelectionChanged.connect(self.get_tree_selection)
    
    def button_handler(self):
        self.btn_connect.clicked.connect(self.pull_device_info)
        self.btn_execute_command.clicked.connect(self.execute_command)
        self.combo_commands.activated.connect(self.update_edit_command)
        self.btn_display_set.clicked.connect(self.show_display_set)
        self.btn_exit.clicked.connect(self.close_application)
        self.btn_add_network.clicked.connect(self.save_display_new_devices)
        self.btn_config_intf.clicked.connect(self.open_interface_diag)
        
    def close_application(self):
        self.close()
    
    def open_interface_diag(self):
        self.ip = self.edit_ip_add.text()
        self.intfDiag = L2IntfConfig(self.ip, self.username, self.password)
        self.intfDiag.show()
        
    ####
    
    def validate_subnet(self):
        if self.edit_new_network.text() == "":
            self.edit_new_network.setText("Network can't be empty!")
            return False
        else:
            if not IPv4Check.check_ip_format(self.edit_new_network.text()):
                self.edit_new_network.setText("Invalid IP Address")
                return False
            else:
                if not IPv4Check.check_valid_ip(self.edit_new_network.text()):
                    self.edit_new_network.setText("Invalid IP Address")
                    return False
                
        if self.edit_snmp_community.text() == "":
            self.edit_snmp_community.setText("Community can't be empty!")
            return False
        
        return True
    
    ## Populate controls on initialization
    
    def get_mysql_devices(self):
        conn = MySQLdb.connect(host="localhost", user="root", password="noway1", db="mynms")
        cur = conn.cursor()
        cur.execute('''
        SELECT hostname FROM devices
        ''')
        devices = cur.fetchall()
        conn.close()
        return [device[0] for device in devices]
    
    def populate_devices_tree(self):
        devices = self.get_mysql_devices()
        self.tree_devices.clear()
        parent = QTreeWidgetItem(self.tree_devices)
        parent.setText(0, "Devices")
        
        for item in devices:
            child = QTreeWidgetItem(parent)
            child.setText(0, item)
    
    def get_tree_selection(self):
        get_selected = self.tree_devices.selectedItems()
        if get_selected:
            base_node = get_selected[0]
            child_node = base_node.text(0)
            conn = MySQLdb.connect(host="localhost", user="root", password="noway1", db="mynms")
            cur = conn.cursor()
            cur.execute('''
            SELECT ip_add FROM devices WHERE hostname=(%s);
            ''',(child_node,)
            )
            ip_address = cur.fetchall()
            conn.close()
            self.edit_ip_add.setText(ip_address[0][0])
            self.ip = ip_address[0][0]
    
    def get_subnet(self):
        net_address = ''
        block = 0
        adder = 0
        network = self.edit_new_network.text()
        network = network.split('/')
        subnet_list = network[0].split('.')
        network_bits = int(network[1])
        bit_values = [128,64,32,16,8,4,2,1]      
        
        if network_bits == 24:
            net_address = subnet_list[0]+'.'+subnet_list[1]+'.'+subnet_list[2]+'.0'
            block = 255
        elif network_bits < 32:            
            for num in range(network_bits-24):
                adder += bit_values[num]
            block = 256-adder
            net_address = subnet_list[0]+'.'+subnet_list[1]+'.'+subnet_list[2]+'.'+ str(int(int(subnet_list[3])/block)*block)
        elif network_bits == 32:
            net_address = network[0]
            block = 1
        return (net_address, block)
    
    def discovery_devices(self, net_address, block):
        conn = Connectivity()
        live_hosts = []
        
        if block == 1:
            if conn.check_connectivity(net_address):
                live_hosts.append(net_address)
                found_msg = QMessageBox()
                found_msg.Icon(QMessageBox.Information)
                found_msg.setWindowTitle("Device Found")
                found_msg.setText(f"{net_address} found and added")
            else:
                not_found_msg = QMessageBox()
                not_found_msg.Icon(QMessageBox.Critical)
                not_found_msg.setWindowTitle("Error")
                not_found_msg.setText(f"{net_address} not reachable or SNMP community not configured")
        else:        
            subnet_4_octets = net_address.split('.')
            subnet_3_octets = subnet_4_octets[0] +'.' + subnet_4_octets[1] +'.'+ subnet_4_octets[2]
            
            for host in range(block-1):
                ip = subnet_3_octets + '.' + str(int(subnet_4_octets[3])+host)
                print(f"test ip: {ip}")
                if conn.check_connectivity(ip):
                    live_hosts.append(ip)
        
        return live_hosts
    
    def save_display_new_devices(self):
        
        if self.validate_subnet():            
            net_add, block = self.get_subnet()
            devices = self.discovery_devices(net_add, block)
            hostnames = []
            conn = MySQLdb.connect(host="localhost", user="root", password="noway1", db="mynms")
            cur = conn.cursor()
            for ip in devices:
                hostname = GetSNMP.get_hostname(ip, self.edit_snmp_community.text())
                vendor = GetSNMP.get_vendor(ip, self.edit_snmp_community.text())
                cur.execute(''' INSERT IGNORE INTO devices(ip_add, hostname, vendor) VALUES(%s, %s, %s) ''', (ip, hostname, vendor))
            conn.commit() 
            self.populate_devices_tree()        

    
    def populate_protocol_combo(self):
        protocols = ["Telnet", "SSH"]
        for protocol in protocols:
            self.combo_protocol.addItem(protocol)
        
        # temparary until Telnet is not implemented
        # when telnet is implemetned, just remove below lines
        
        self.combo_protocol.setCurrentIndex(0)
        self.combo_protocol.setEnabled(True)
    
    def populate_device_type_combo(self):
        devices = ["Cisco IOS", "Junos"]
        for device in devices:
            self.combo_device_type.addItem(device)
    
    def show_display_set(self):
        self.display_set = True
        self.execute_command()
        
    
    def pull_device_info(self):       
    
       
        self.hostname = self.edit_ip_add.text()
        self.protocol = self.combo_protocol.currentText()
        self.username = self.edit_username.text()
        self.password = self.edit_password.text()
        self.device_type = self.combo_device_type.currentText()
        device_type = self.combo_device_type.currentText()
        
        if self.protocol == "Telnet":
            self.connection_test = cisco.connection_test_telnet(self.hostname, self.username, self.password)
        elif self.protocol == "SSH":
            self.connection_test = cisco.connection_test_ssh(self.hostname, self.username, self.password)
        
            
        if self.connection_test == True:
            
             # disable username/password fields
            self.edit_username.setEnabled(False)
            self.edit_password.setEnabled(False)
            # connected message instead of error
            self.label.setText("Connected")
            self.btn_connect.setEnabled(False)
            #self.btn_connect.setText("Disconnect")
            self.combo_device_type.setEnabled(False)
            
            if device_type == "Cisco IOS":
                
                if self.protocol == "SSH":    
                     
                    device_hostname = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show run | in hostname")                       
                    device_hostname = device_hostname[0].split(' ')[1]
                    self.lbl_hostname.setText(device_hostname)
                   
                    
                    ios_version = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show version | in Version")
                    ios_version = ios_version[0]
                    self.lbl_ios_version.setText(ios_version)
        
                    
                    cpu_status = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show proc cpu | in CPU")
                    cpu_status = cpu_status[0].strip('\n')       
                    self.lbl_cpu_utilization.setText(cpu_status)
        
                    
                    uptime = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show version | in time")
                    uptime = uptime[0].strip('\n')
                    self.lbl_uptime.setText(uptime)
                    
                elif self.protocol == "Telnet":
                    
                    device_hostname = cisco.show_telnet_cisco(self.hostname, self.username, self.password, "show run | in hostname")                       
                    device_hostname = device_hostname[-3].split(' ')[1]
                    self.lbl_hostname.setText(device_hostname)
                    
                    ios_version = cisco.show_telnet_cisco(self.hostname, self.username, self.password, "show version | in Version")
                    ios_version = ios_version[-3]
                    self.lbl_ios_version.setText(ios_version)
                    
                    cpu_status = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show proc cpu | in CPU")
                    cpu_status = cpu_status[-3].strip('\n')       
                    self.lbl_cpu_utilization.setText(cpu_status)
                    
                    uptime = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show version | in time")
                    uptime = uptime[-3].strip('\n')
                    self.lbl_uptime.setText(uptime)
                
                
            elif device_type == "Junos":
                if self.protocol == "SSH":
                    device_hostname = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show version | match Hostname")                       
                    device_hostname = device_hostname[0].split(' ')[1]
                    self.lbl_hostname.setText(device_hostname)
                    
                    ios_version = "before"
                    ios_version = cisco.show_cmd_ssh(self.hostname, self.username, self.password, 'show version | match "Base OS Boot"')
                    ios_version = ios_version[0]
                    #print(ios_version)
                    self.lbl_ios_version.setText(ios_version)
                    
                    uptime = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show system uptime")
                    for output in uptime:
                        if "up" in output:
                            self.lbl_uptime.setText(output)

        else:
            self.label.setText("Couldn't connect, Check username/password, connectivity to host")
    
    def populate_commands_combo(self):
        commands = [
            "show running-config",
            "show configuration section",
            "show interfaces status",
            "show routing table",
            "show neighbors",
            "show arp",
            "custom command",            
            ]
        for command in commands:
            self.combo_commands.addItem(command)
    
    def update_edit_command(self):
        
        if self.combo_commands.currentText() == "show configuration section":
            self.edit_custom_command.setPlaceholderText("What section of configuration you want to view?")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "show routing table":
            self.edit_custom_command.setPlaceholderText("Enter prefix for details or leave empty")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "show neighbors":
            self.edit_custom_command.setPlaceholderText("Enter interface-id or detail keyword to see details or leave empty")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "show arp":
            self.edit_custom_command.setPlaceholderText("Enter IP or leave empty")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "custom command":
            self.edit_custom_command.setPlaceholderText("Enter custom command")
            self.edit_custom_command.setEnabled(True)
        else:
            self.edit_custom_command.setText("")
            self.edit_custom_command.setEnabled(False)                                   
            
      
    
    def cisco_show_run(self):
        
        if self.device_type == "Cisco IOS":
            command = "show run"
        elif self.device_type == "Junos":
            if self.display_set == True:
                command = "show configuration | display set"
                self.display_set = False
            else:
                command = "show configuration"
            
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()       
        for config in run_config:
            self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_run_section(self):
        
        section = self.edit_custom_command.text()
        
        if self.combo_device_type.currentText() == "Cisco IOS":
            if section:                          
                command = "Show run | section " + section
            else:
                command = "show run"
        elif self.combo_device_type.currentText() == "Junos":
            if self.display_set == True:
                command = "show configuration " + section + " | display set"
                self.display_set = False
            else:
                command = "show configuration " + section
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
            self.ptedit_cmd_output.appendPlainText("No configurations found for this section")
    
    def cisco_interfaces_status(self):
        
        if self.device_type == "Cisco IOS":                 
            run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show ip int brief")
        elif self.device_type == "Junos":
            run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show interface terse")
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_routing_table(self):
        
        if self.device_type == "Cisco IOS":
            command = "show ip route "
        elif self.device_type == "Junos":
            command = "show route "
        
        if self.edit_custom_command.text():
            command = command + self.edit_custom_command.text()        
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_cdp_neighbor(self):
        
        if self.device_type == "Cisco IOS":
            command = "show cdp neighbor "
        elif self.device_type == "Junos":
            command = "show lldp neighbor "
        
        if self.edit_custom_command.text():
            command = command + self.edit_custom_command.text()
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
                self.ptedit_cmd_output.appendPlainText("NO neighbors found")
    
    def cisco_show_arp(self):
        
        if self.device_type == "Cisco IOS":
            command = "show ip arp "
            if self.edit_custom_command.text():
                command = command + self.edit_custom_command.text()  
        elif self.device_type == "Junos":
            command = "show arp "
            if self.edit_custom_command.text():
                command = command + "hostname " + self.edit_custom_command.text()  
        
             
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
                self.ptedit_cmd_output.appendPlainText("No arp entry found for this host.")
                
    def cisco_custom_command(self):
               
        if self.edit_custom_command.text():
            command = self.edit_custom_command.text()
        else:
            self.edit_custom_command.setPlaceholderText("Please enter a command")
            return
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
                self.ptedit_cmd_output.appendPlainText("Invalid command")         
       
    
    def execute_command(self):
        
        if self.label.text() == "Connected":
            selection = self.combo_commands.currentText()
            device_type = self.combo_device_type.currentText()
            
            if selection == "show running-config":
                self.cisco_show_run()
            elif selection == "show configuration section":
                 self.cisco_show_run_section()
            elif selection == "show interfaces status":
                self.cisco_interfaces_status()
            elif selection == "show routing table":
                self.cisco_show_routing_table()
            elif selection == "show neighbors":
                self.cisco_show_cdp_neighbor()
            elif selection == "show arp":
                self.cisco_show_arp()
            else:
                self.cisco_custom_command()    
                
       
    



def main():
    
    app = QApplication(argv)
    
    myapp = MainWindow()
    myapp.show()
    
    app.exec_()
    
if __name__ == "__main__":
    main()


