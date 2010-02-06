# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from browseWidget_ui import Ui_browseWidget
from flickcharm import *

class BrowseWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_browseWidget()
        self.ui.setupUi(self)

        #setup flickcharm
        self.trackCharm = FlickCharm()
        self.trackCharm.activateOn(self.ui.trackList)
        self.ui.trackList.setVerticalScrollMode(\
                self.ui.trackList.ScrollPerPixel)
        self.artistCharm = FlickCharm()
        self.artistCharm.activateOn(self.ui.artistList)
        self.ui.artistList.setVerticalScrollMode(\
                self.ui.artistList.ScrollPerPixel)
        self.genreCharm = FlickCharm()
        self.genreCharm.activateOn(self.ui.genreList)
        self.ui.genreList.setVerticalScrollMode(\
                self.ui.genreList.ScrollPerPixel)
    
    def addContinue(self):
        self._addToPlaylist()

    def addClose(self):
        if self._addToPlaylist():
            self.cancel()

    def switchToSearch(self):
        pass

    def cancel(self):
        self.parent().gotoMainWidget()
