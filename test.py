#!/usr/bin/python3
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUiType
import sys

ui,_ = loadUiType('test.ui')


class MainApp(QMainWindow, ui):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.populate_list()
        
    
    def populate_list(self):
        self.listWidget.addItem("Shahzad")
        for name in ["Shahzad", "Qadir", "s/o Qadir Baksh"]:
            self.plainTextEdit.appendPlainText(name)

def main():
    
    app = QApplication(sys.argv)
    
    myapp = MainApp()
    myapp.show()
    
    app.exec_()

if __name__ == "__main__":
    main()

