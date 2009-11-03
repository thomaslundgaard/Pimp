# -*- coding: utf-8 -*-
import os,sys
from PyQt4 import QtCore,QtGui
from mainWindow import MainWindow

def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

 
