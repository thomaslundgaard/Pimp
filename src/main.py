#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from PyQt4 import QtCore,QtGui
from mainWindow import MainWindow

def main():
    app = QtGui.QApplication(sys.argv)
    scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    QtGui.qApp.pixmapsPath=scriptPath+"/../pixmaps"
    QtGui.qApp.resourcesPath=scriptPath+"/../resources"

    app.setWindowIcon(QtGui.QIcon(QtGui.qApp.pixmapsPath+"/icon16.png"))
    app.setOrganizationName("pympdjuke");
    app.setApplicationName("PyMpdJuke");

    app.styleSheet = QtCore.QFile(QtGui.qApp.resourcesPath+"/stylesheet.qss")
    app.styleSheet.open(QtCore.QIODevice.ReadOnly)
    app.setStyleSheet( str(app.styleSheet.readAll()) )
    app.styleSheet.close()

    window = MainWindow()
    window.setWindowTitle("PyMPDJuke")
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

