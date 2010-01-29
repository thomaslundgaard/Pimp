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
        self.setStyleSheet("\
                background: qlineargradient(spread:pad, x1:1, y1:1, x2:1,\
                    y2:0, stop:0.565217 rgba(50, 50, 50, 255), \
                    stop:1 rgba(100, 100, 100, 255)); \
                font: 14pt \"Sans Serif\"; \
                color: rgb(237, 237, 237);")

        self.server = ServerInterface()
        self.mainWidget = MainWidget(self)
        self.addWidget(self.mainWidget)
        self.searchWidget = SearchWidget(self)
        self.addWidget(self.searchWidget)
        self.server.connect()
        self.startTimer(1000)

    def gotoFullscreen(self):
        self.isFullscreen = True
        self.showFullScreen()
        self.raise()

    def leaveFullscreen(self):
        self.isFullscreen = False
        self.showNormal()
        self.showMinimized()

    def closeEvent(self, event):
        if self.isFullscreen:
            QtCore.QEvent.ignore(event)

    def changeEvent(self, event):
        if QtGui.qApp.activeWindow() == None and self.isFullscreen:
            self.showFullScreen()
            self.raise()

    def timerEvent(self, event):
        if QtGui.qApp.activeWindow() == None and self.isFullscreen:
            self.showFullScreen()
            self.raise()

    def gotoMainWidget(self):
        self.setCurrentWidget (self.mainWidget)

    def gotoSearchWidget(self):
        self.setCurrentWidget (self.searchWidget)

