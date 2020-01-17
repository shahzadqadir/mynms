from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QMessageBox
from PyQt5.uic import loadUiType
from cisco import show_cmd_ssh, config_cmd_ssh
import sys
#from ansible.modules.network import interface
from time import sleep

intf, _ = loadUiType("l2_interface_config.ui")

class L2IntfConfig(QWidget,  intf):
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
        self.btn_current_config.clicked.connect(self.show_current_config)
        self.btn_build_config.clicked.connect(self.config_preview)
        self.btn_write_config.clicked.connect(self.write_cisco_config)
        self.btn_close.clicked.connect(self.close_intf_dialog)        
    
    def current_config(self):
        selection = self.cmb_interfaces.currentText()
        interface = selection.split(' ')[0]
        current_config_list = []
        command = "show run interface " + interface
        int_config = show_cmd_ssh(self.ip, self.username, self.password, command)
        for line in int_config:
            current_config_list.append(line.replace("\r","").strip("\n"))
        return current_config_list
    
    def show_current_config(self):
        current_config = self.current_config()
        current_config_str = "\n"
        current_config_str = current_config_str.join(current_config)
        #
        #print(current_config)
        #
        curr_config_diag = QMessageBox()
        curr_config_diag.setWindowTitle("Current Configuration ...")
        curr_config_diag.setText(current_config_str)
        curr_config_diag.setModal(True)
        curr_config_diag.addButton(QMessageBox.Ok)
        curr_config_diag.exec() 
    
    
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
            config_list.append(f"switchport access vlan {access_vlan}")
        trunk_vlans = self.edit_trunk_vlans.text()
        if trunk_vlans:
            config_list.append(f"switchport trunk allowed vlan {trunk_vlans}")
        if self.check_shutdown.isChecked():
            config_list.append("shutdown")
        else:
            config_list.append("no shutdown")
        
        return config_list
    
    def config_preview(self):
        configs = self.build_config_cisco()
        config_str = "\n"
        config_str = config_str.join(configs)
        #
        preview_diag = QMessageBox()
        preview_diag.setWindowTitle("Configuration Preview")
        preview_diag.setText(config_str)
        preview_diag.setModal(True)
        preview_diag.addButton(QMessageBox.Ok)
        preview_diag.exec()
    
    def write_cisco_config(self):
        self.lbl_config_status.setText("WRITING CONFIGS NOW...")
        sleep(1)
        cmd_list = self.build_config_cisco()
        if config_cmd_ssh(self.ip, self.username, self.password, cmd_list):
            success_diag = QMessageBox()
            success_diag.Icon(QMessageBox.Information)
            success_diag.setWindowTitle("Success")
            success_diag.setText("Configurations done successfully.")
            success_diag.exec()
            self.lbl_config_status.setText("")
    
    def close_intf_dialog(self):
        self.close()

 
# def main():
#     app = QApplication(sys.argv)
#         
#     myapp = L2IntfConfig("192.168.10.2", "nms", "cisco")
#     myapp.show()
#         
#     app.exec_()
#     
# if __name__ == "__main__":
#     main()
            
         
        