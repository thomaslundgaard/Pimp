# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from searchWidget import SearchWidget
from mainWidget import MainWidget

class MainWindow(QtGui.QStackedWidget):
    def __init__(self):
        QtGui.QStackedWidget.__init__(self)
        self.mainWidget = MainWidget(self)
        self.addWidget(self.mainWidget)
        self.searchWidget = SearchWidget(self)
        self.addWidget(self.searchWidget)

    def gotoMainWidget(self):
        self.setCurrentWidget (self.mainWidget)

    def gotoSearchWidget(self):
        self.setCurrentWidget (self.searchWidget)

