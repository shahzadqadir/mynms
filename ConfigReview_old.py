#!/usr/bin/python3
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMainWindow, QApplication
from sys import argv
from PyQt5.Qt import QTableWidgetItem, QWidget
import cisco

ui,_ = loadUiType('ConfigReview.ui')

class MainWindow(QMainWindow, ui):
    def __init__(self):
        self.hostname = ""
        self.protocol = ""
        self.username = ""
        self.password = ""     
        
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.populate_protocol_combo()
        self.populate_device_type_combo()
        self.button_handler()
        self.populate_commands_combo()
    
    def button_handler(self):
        self.btn_connect.clicked.connect(self.pull_device_info)
        self.btn_execute_command.clicked.connect(self.execute_command)        
    
    
    def populate_protocol_combo(self):
        protocols = ["Telent", "SSH"]
        for protocol in protocols:
            self.combo_protocol.addItem(protocol)
    
    def populate_device_type_combo(self):
        devices = ["Cisco IOS", "Junos"]
        for device in devices:
            self.combo_device_type.addItem(device)
    
    def pull_device_info(self):
        self.hostname = self.edit_ip_add.text()
        self.protocol = self.combo_protocol.currentText()
        self.username = self.edit_username.text()
        self.password = self.edit_password.text()
        device_type = self.combo_device_type.currentText()
        
        device_hostname = cisco.show_cmd(self.hostname, self.username, self.password, "show run | in hostname")
        device_hostname = (self.hostname[0].split(' ')[-1]).strip('\n')
        self.lbl_hostname.setText(device_hostname)
        
        ios_version = cisco.show_cmd(self.hostname, self.username, self.password, "show version | in Version")
        ios_version = ios_version[0]
        self.lbl_ios_version.setText(ios_version)
        
        cpu_status = cisco.show_cmd(self.hostname, self.username, self.password, "show proc cpu | in CPU")
        cpu_status = cpu_status[0].strip('\n')       
        self.lbl_cpu_utilization.setText(cpu_status)
        
        uptime = cisco.show_cmd(self.hostname, self.username, self.password, "show version | in time")
        uptime = uptime[0].strip('\n')
        self.lbl_uptime.setText(uptime)
    
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
    
    def cisco_show_run(self):
        run_config = cisco.show_cmd(self.hostname, self.username, self.password, "show run")
        
        self.ptedit_cmd_output.clear()       
        for config in run_config:
            self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_run_section(self):
        section = self.edit_custom_command.text()
        command = "Show run | section " + section
        
        run_config = cisco.show_cmd(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
            self.ptedit_cmd_output.appendPlainText("No configurations found for this section")
    
    def cisco_interfaces_status(self):
        
        run_config = cisco.show_cmd(self.hostname, self.username, self.password, "show ip int brief")
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_routing_table(self):
        
        if self.edit_custom_command.text():
            command = "show ip route " + self.edit_custom_command.text()
        else:
            command = "show ip route"
        
        run_config = cisco.show_cmd(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_cdp_neighbor(self):
        
        if self.edit_custom_command.text():
            command = "show cdp neighbor " + self.edit_custom_command.text()
        else:
            command = "show cdp neighbor"
        
        run_config = cisco.show_cmd(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_arp(self):
        
        if self.edit_custom_command.text():
            command = "show ip arp | inc " + self.edit_custom_command.text()
        else:
            command = "show ip arp"
        
        run_config = cisco.show_cmd(self.hostname, self.username, self.password, command)
        
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
        
        run_config = cisco.show_cmd(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
                self.ptedit_cmd_output.appendPlainText("Invalid command")         
       
    
    def execute_command(self):
        selection = self.combo_commands.currentText()
        device_type = self.combo_device_type.currentText()
        
        if self.protocol == "SSH":        
            if selection == "show running-config" and device_type == "Cisco IOS":
                self.cisco_show_run()
            elif selection == "show configuration section":
                self.edit_custom_command.setPlaceholderText("section of configuration you want to view")
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


