# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore,QtGui
from mainWindow import MainWindow

def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("res/karaoke.png"))
    app.setOrganizationName("Blupix");
    app.setApplicationName("PyMpdJuke");

    #FIXME: Stylesheet to make LineEdit have transparent\
    #       background
    app.setStyleSheet("QLineEdit {border-style: groove;\
            border-width:2px;}")
    #QtCore.Qt.setOrganizationDomain("mysoft.com");
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
 
