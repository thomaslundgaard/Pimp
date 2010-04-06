#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Pimp - A mpd-frontend to be used as a jukebox at parties.
# Copyright (C) 2010 Peter Bjørn
# Copyright (C) 2010 Thomas Lundgaard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os
from PyQt4 import QtCore,QtGui
from mainWindow import MainWindow

def main():
    app = QtGui.QApplication(sys.argv)
    scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    QtGui.qApp.pixmapsPath=scriptPath+"/../pixmaps"
    QtGui.qApp.resourcesPath=scriptPath+"/../resources"

    app.setWindowIcon(QtGui.QIcon(QtGui.qApp.pixmapsPath+"/icon.png"))
    app.setOrganizationName("pimp");
    app.setApplicationName("Pimp");

    app.styleSheet = QtCore.QFile(QtGui.qApp.resourcesPath+"/stylesheet.qss")
    app.styleSheet.open(QtCore.QIODevice.ReadOnly)
    app.setStyleSheet( str(app.styleSheet.readAll()) )
    app.styleSheet.close()

    window = MainWindow()
    window.setWindowTitle("Pimp")
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

