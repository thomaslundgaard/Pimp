# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from searchWidget_ui import Ui_SearchWidget
from virtualKeyboard import VirtualKeyboard
from settings import Settings
from helperFunctions import asciify
from flickcharm import *
from serverInterface import ServerInterfaceError
from serverInterface import AddToPlaylistError

class SearchWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SearchWidget()
        self.ui.setupUi(self)
        vkb = VirtualKeyboard()
        vkb.setInputLine(self.ui.searchLine)
        self.ui.vbox.addWidget(vkb)
        self.charm = FlickCharm()
        self.charm.activateOn(self.ui.resultList)
        
        self.keyWords = []
        self.resultList = []

        #set stretch factors
        self.ui.vbox.setStretchFactor(vkb,6)
        self.ui.vbox.setStretchFactor(self.ui.gridLayout,5)
        
    def addContinue(self):
        self._addToPlaylist()

    def addClose(self):
        if self._addToPlaylist():
            self.cancel()

    def switchToBrowse(self):
        self.parent().gotoBrowseWidget()

    def cancel(self):
        self.parent().gotoMainWidget()

    def searchTextChanged(self, text):
        words = unicode(text.toUtf8(), 'utf-8').split()
        keyWords = [asciify(word.lower().strip()) for word in words if len(word) >= 2]

        self.clearResults()
        if len(keyWords) > 0:
            for result in QtGui.qApp.server.searchDBtag(True,*keyWords):
                self.resultList.append(result)
                self.ui.resultList.addItem("%s - %s  (%i:%02i)" % \
                        (result['artist'] , result['title'],\
                        result['time']/60, result['time']%60 ))

    def clearResults(self):
        self.resultList = []
        self.ui.resultList.clear()

    def _addToPlaylist(self):
        row = self.ui.resultList.currentRow()
        if row < 0:
            return False
        try:
            entry = self.resultList[row]
        except IndexError:
            return False
        try:
            answer = QtGui.qApp.server.addToPlaylist(entry['file'])
            self.ui.infoLabel.setText("Added %s - %s" % \
                    (entry['artist'] , entry['title']))
            self.ui.infoLabel.show()
            return True
        except ServerInterfaceError:
            return False
        except AddToPlaylistError as inst:
            self.ui.infoLabel.setText(inst.args[0])
            self.ui.infoLabel.show()
            return False

