# -*- coding: utf-8 -*-
import os,sys
from PyQt4 import QtCore,QtGui
from ui_mainClass import Ui_MainClass

def main():
    app = QtGui.QApplication(sys.argv)
    window = Ui_MainClass()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

