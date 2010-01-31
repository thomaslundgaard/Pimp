# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from serverInterface import ServerInterface
from searchWidget import SearchWidget
from mainWidget import MainWidget

class MainWindow(QtGui.QStackedWidget):
    def __init__(self):
        QtGui.QStackedWidget.__init__(self)
        self.isFullscreen = False
        self.resize(800, 600)
        
        self.server = ServerInterface()
        self.mainWidget = MainWidget(self)
        self.addWidget(self.mainWidget)
        self.searchWidget = SearchWidget(self)
        self.addWidget(self.searchWidget)
        self.server.connect()
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
        self.showMinimized()
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
        self.setCurrentWidget (self.searchWidget)

