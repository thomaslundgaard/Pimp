# -*- coding: utf-8 -*-
import socket
from PyQt4 import QtCore, QtGui
from searchWidget import SearchWidget
from mainWidget import MainWidget
from browseWidget import BrowseWidget
from serverInterface import *

class MainWindow(QtGui.QStackedWidget):
    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)
        self.isFullscreen = False
        self.resize(800, 600)
        
        socket.setdefaulttimeout(2)
        self.server = ServerInterface(self)
        QtGui.qApp.server = self.server
        self.mainWidget = MainWidget(self)
        self.addWidget(self.mainWidget)
        self.searchWidget = SearchWidget(self)
        self.addWidget(self.searchWidget)
        self.browseWidget = BrowseWidget(self)
        self.addWidget(self.browseWidget)
        QtGui.qApp.server.sigDisconnected.connect(self.gotoMainWidget)
        QtGui.qApp.server.connect()
        self.startTimer(1000)

    def gotoFullscreen(self):
        self.isFullscreen = True
        self.mainWidget.ui.adminBtn.setText ("Admin /\nLeave fullscreen")
        self.mainWidget.ui.fullscreenBtn.setVisible(False)
        self.showFullScreen()
        self.activateWindow()
        self.raise_()

    def leaveFullscreen(self):
        self.isFullscreen = False
        self.showNormal()
        self.mainWidget.ui.adminBtn.setText ("Admin")
        self.mainWidget.ui.fullscreenBtn.setVisible(True)

    def closeEvent(self, event):
        if self.isFullscreen:
            QtCore.QEvent.ignore(event)

    def changeEvent(self, event):
        if QtGui.qApp.activeWindow() == None and self.isFullscreen:
            self.showFullScreen()
            self.activateWindow()
            self.raise_()

    def timerEvent(self, event):
        if QtGui.qApp.activeWindow() == None and self.isFullscreen:
            self.showFullScreen()
            self.activateWindow()
            self.raise_()

    def gotoMainWidget(self):
        self.setCurrentWidget (self.mainWidget)

    def gotoSearchWidget(self):
        self.searchWidget.clearResults()
        self.searchWidget.ui.searchLine.clear()
        self.searchWidget.ui.infoLabel.hide()
        self.setCurrentWidget (self.searchWidget)
        self.searchWidget.ui.searchLine.setFocus()
    def gotoBrowseWidget(self):
        self.setCurrentWidget(self.browseWidget)
        self.browseWidget.clearSelection()

