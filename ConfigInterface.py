from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QMessageBox
from PyQt5.uic import loadUiType
from cisco import show_cmd_ssh, config_cmd_ssh
import sys
#from ansible.modules.network import interface
from time import sleep

l2intf, _ = loadUiType("l2_interface_config.ui")
l3intf, _ = loadUiType("l3_interface_config.ui")
l3intfjunos, _ = loadUiType("l3_intf_config_junos.ui")

class L2IntfConfig(QWidget,  l2intf):
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

class L3IntfConfig(QWidget, l3intf):
    def __init__(self, ip, username, password):
        QWidget.__init__(self)
        self.ip = ip
        self.username = username
        self.password = password
        self.setupUi(self)
        self.populate_intf_combo()
        self.populate_nat_combo()
        self.button_handler()
        
    def button_handler(self):
        self.btn_current_config.clicked.connect(self.show_current_config)
        self.btn_build_config.clicked.connect(self.config_preview)
        self.btn_close.clicked.connect(self.close_intf_dialog)
        self.btn_write_config.clicked.connect(self.write_cisco_config)
    
    def populate_intf_combo(self):
        self.cmb_interfaces.clear()
        output = show_cmd_ssh(self.ip, self.username, self.password, "show ip int brief")
        intf_list = []
        for row in output:
            self.cmb_interfaces.addItem(row.replace("\r","").strip("\n"))
    
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
        
    def populate_nat_combo(self):
        options = ["", "Inside", "Outside"]
        for option in options:
            self.combo_nat.addItem(option)
            
    def build_config_cisco(self):
        selection = self.cmb_interfaces.currentText()
        interface = selection.split(' ')[0]
        config_list = ["terminal length 0", "configure terminal"]
        config_list.append(f"interface {interface}")
        description = self.edit_l3_desc.text()
        if description:
            config_list.append(f"description {description}")
        l3_ip_add = self.edit_ip_address.text()
        l3_subnet_mask = self.edit_mask.text()
        if l3_ip_add and l3_subnet_mask:
            config_list.append(f"ip address {l3_ip_add} {l3_subnet_mask}")
        ip_helper = self.edit_ip_helper.text()
        if ip_helper:
            config_list.append(f"ip helper {ip_helper}")
        acl_in = self.edit_acl_in.text()
        if acl_in:
            config_list.append(f"access-class {acl_in} in")        
        acl_out = self.edit_acl_out.text()
        if acl_out:
            config_list.append(f"access-class {acl_out} out")
        nat_operation = self.combo_nat.currentText()
        if nat_operation:
            if nat_operation == "Inside":
                config_list.append("ip nat inside")
            elif nat_operation == "Outside":
                config_list.append("ip nat outside")     
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

class L3IntfConfigJunos(QWidget, l3intfjunos):
    def __init__(self, ip, username, password):
        QWidget.__init__(self)
        self.ip = ip
        self.username = username
        self.password = password
        self.setupUi(self)
        self.populate_intf_combo()
        self.button_handler()
        self.cmb_interfaces.currentIndexChanged.connect(self.update_intf_textbox)
        
    def button_handler(self):
        self.btn_current_config.clicked.connect(self.show_current_config)
        self.btn_build_config.clicked.connect(self.config_preview)
        self.btn_close.clicked.connect(self.close_intf_dialog)
        self.btn_write_config.clicked.connect(self.write_junos_config)
    
    def populate_intf_combo(self):
        self.cmb_interfaces.clear()
        output = show_cmd_ssh(self.ip, self.username, self.password, "show interfaces terse")
        intf_list = []
        for row in output:
            self.cmb_interfaces.addItem(row.replace("\r","").strip("\n"))
    
    def current_config(self):
        selection = self.cmb_interfaces.currentText()
        interface = selection.split(' ')[0]
        current_config_list = []
        command = "show configuration interfaces " + interface
        int_config = show_cmd_ssh(self.ip, self.username, self.password, command)
        for line in int_config:
            current_config_list.append(line.replace("\r","").strip("\n"))
        return current_config_list
    
    def show_current_config(self):
        current_config = self.current_config()
        current_config_str = "\n"
        current_config_str = current_config_str.join(current_config)
        #
#         print(current_config)
        #
        curr_config_diag = QMessageBox()
        curr_config_diag.setWindowTitle("Current Configuration ...")
        curr_config_diag.setText(current_config_str)
        curr_config_diag.setModal(True)
        curr_config_diag.addButton(QMessageBox.Ok)
        curr_config_diag.exec()
    
    def update_intf_textbox(self):
        selection = self.cmb_interfaces.currentText()
        interface = selection.split(' ')[0]
        self.edit_ip_address_2.setText(interface)
    
    def check_input_filters(self, input_filter):
        output = show_cmd_ssh(self.ip, self.username, self.password, "show configuration firewall | display set")
        for pointer in output:
            if input_filter in pointer:
                return True
        return False
    
    def check_output_filters(self, output_filter):
        output = show_cmd_ssh(self.ip, self.username, self.password, "show configuration firewall | display set")
        for pointer in output:
            if output_filter in pointer:
                return True
        return False        

            
    def build_config_junos(self):
        config_list = ["configure"]
#         selection = self.cmb_interfaces.currentText()
#         interface = selection.split(' ')[0]
        interface = self.edit_ip_address_2.text().split('.')[0]
        unit = self.edit_unit.text()
        description = self.edit_l3_desc.text()
        l3_ip_add = self.edit_ip_address.text()
        l3_net_bits = self.edit_mask.text()     
        filter_in = self.edit_acl_in.text()
        filter_out = self.edit_acl_out.text()  

        
        if interface:
            if l3_ip_add and l3_net_bits:
                config_list.append(f"set interface {interface} unit {unit} family inet address {l3_ip_add}/{l3_net_bits}")
                if filter_in:
                    config_list.append(f"set interface {interface} unit {unit} family inet filter input {filter_in}")
                if filter_out:
                    config_list.append(f"set interface {interface} unit {unit} family inet filter output {filter_out}")
        
                if self.check_shutdown.isChecked():
                    config_list.append(f"set interface {interface} unit {unit} disable")
                config_list.append("commit")
            else:
                    return ["Please","Enter","a","valid","ip","address","and","subnet","mask"]
        else:
                return ["Please","select", "an", "interface", "from", "the", "list"]         

        return config_list
    
    def config_preview(self):
        configs = self.build_config_junos()
#         print(configs)
        config_str = "\n"
        config_str = config_str.join(configs)
        #
        preview_diag = QMessageBox()
        preview_diag.setWindowTitle("Configuration Preview")
        preview_diag.setText(config_str)
        preview_diag.setModal(True)
        preview_diag.addButton(QMessageBox.Ok)
        preview_diag.exec()
        
    def write_junos_config(self):
        
        if not self.check_input_filters(self.edit_acl_in.text()):
            in_filter_error_diag = QMessageBox()
            in_filter_error_diag.Icon(QMessageBox.Critical)
            in_filter_error_diag.setWindowTitle("Error")
            in_filter_error_diag.setText("Input filter not configured on device, please check")
            in_filter_error_diag.exec()
            return False
        
        if not self.check_output_filters(self.edit_acl_out.text()):
            in_filter_error_diag = QMessageBox()
            in_filter_error_diag.Icon(QMessageBox.Critical)
            in_filter_error_diag.setWindowTitle("Error")
            in_filter_error_diag.setText("Output filter not configured on device, please check")
            in_filter_error_diag.exec()
            return False
        
        cmd_list = self.build_config_junos()
        if config_cmd_ssh(self.ip, self.username, self.password, cmd_list):
            success_diag = QMessageBox()
            success_diag.Icon(QMessageBox.Information)
            success_diag.setWindowTitle("Success")
            success_diag.setText("Configurations done successfully.")
            success_diag.exec()
            #self.lbl_config_status.setText("")
    
    def close_intf_dialog(self):
        self.close() 
        
# def main():
#     app = QApplication(sys.argv)
#          
#     myapp = L3IntfConfigJunos("192.168.10.31", "nms", "cisco123")
#     myapp.show()
#          
#     app.exec_()
#      
# if __name__ == "__main__":
#     main()
#                
#            
          