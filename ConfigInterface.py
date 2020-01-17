from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.uic import loadUiType
from cisco import show_cmd_ssh
import sys
from ansible.modules.network import interface

intf, _ = loadUiType("config_interface.ui")

class IntfConfig(QWidget,  intf):
    def __init__(self, ip, username, password):
        QWidget.__init__(self)
        self.setupUi(self)
        self.button_handler()
        self.ip = ip
        self.username = username
        self.password = password
        self.populate_intf_combo()
        self.populate_speed_combo()
        self.popuate_duplex_combo()
        self.populate_mode_combo()
        
    def button_handler(self):
        self.btn_current_config.clicked.connect(self.current_config)
        self.btn_build_config.clicked.connect(self.build_config_cisco)        
    
    def current_config(self):
        selection = self.cmb_interfaces.currentText()
        interface = selection.split(' ')[0]
        command = "show run interface " + interface
        int_config = show_cmd_ssh(self.ip, self.username, self.password, command)
        for line in int_config:
            print(line)  
    
    
    def populate_intf_combo(self):
        self.cmb_interfaces.clear()
        output = show_cmd_ssh(self.ip, self.username, self.password, "show ip int brief")
        intf_list = []
        for row in output:
            self.cmb_interfaces.addItem(row.replace("\r","").strip("\n"))
    
    def populate_speed_combo(self):
        speeds = ['10','100','1000']
        for speed in speeds:
            self.cmb_speed.addItem(speed)
    
    def popuate_duplex_combo(self):
        duplex = ['auto', 'half', 'full']
        for item in duplex:
            self.cmb_duplex.addItem(item)
    
    def populate_mode_combo(self):
        modes = ['access', 'trunk']
        for mode in modes:
            self.cmb_mode.addItem(mode)
    
    def build_config_cisco(self):
        selection = self.cmb_interfaces.currentText()
        interface = selection.split(' ')[0]
        config_list = ["terminal length 0", "configure terminal"]
        config_list.append(f"interface {interface}")
        description = self.edit_desc.text()
        config_list.append(f"description {description}")
        speed = self.cmb_speed.currentText()
        config_list.append(f"speed {speed}")
        duplex = self.cmb_duplex.currentText()
        config_list.append(f"duplex {duplex}")
        mode = self.cmb_mode.currentText()
        config_list.append(f"switchport mode {mode}")
        access_vlan = self.edit_access_vlan.text()
        if access_vlan:
            config_list.append(f"swichport access vlan {access_vlan}")
        trunk_vlans = self.edit_trunk_vlans.text()
        if trunk_vlans:
            config_list.append(f"switchport trunk allowed vlan {trunk_vlans}")
        print(config_list)

def main():
    app = QApplication(sys.argv)
     
    myapp = IntfConfig("192.168.10.2", "nms", "cisco")
    myapp.show()
     
    app.exec_()
 
if __name__ == "__main__":
    main()
          
        
        