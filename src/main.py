# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore,QtGui
from mainWindow import MainWindow

def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("../pixmaps/karaoke.png"))
    app.setOrganizationName("Blupix");
    app.setApplicationName("PyMpdJuke");

    app.styleSheet = QtCore.QFile("../resources/stylesheet.qss")
    app.styleSheet.open(QtCore.QIODevice.ReadOnly)
    app.setStyleSheet( str(app.styleSheet.readAll()) )
    app.styleSheet.close()

    window = MainWindow()
    window.setWindowTitle("PyMPDJuke")
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

