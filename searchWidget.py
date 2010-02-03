# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from searchWidget_ui import Ui_SearchWidget
from virtualKeyboard import VirtualKeyboard
from settings import Settings
from helperFunctions import asciify

class SearchWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SearchWidget()
        self.ui.setupUi(self)
        vkb = VirtualKeyboard()
        vkb.setInputLine(self.ui.searchLine)
        self.ui.vbox.addWidget(vkb)
        
        self.keyWords = []
        self.resultList = []

        #set stretch factors
        self.ui.vbox.setStretchFactor(vkb,4)
        self.ui.vbox.setStretchFactor(self.ui.hbox,1)
        self.ui.vbox.setStretchFactor(self.ui.resultList,2)
        
    def addContinue(self):
        self._addToPlaylist()
    def addClose(self):
        self._addToPlaylist()
        self.cancel()
    def cancel(self):
        self.parentWidget().gotoMainWidget()
        self.clearResults()
        self.ui.searchLine.clear()
    def searchTextChanged(self, text):
        words = str(text).split()
        keyWords = [asciify(word.lower().strip()) for word in words if len(word) >= 2]

        if len(keyWords) > 0:

            self.clearResults()
            for result in self.parent().server.searchDB(keyWords):
                self.resultList.append(result)
                self.ui.resultList.addItem("%s - %s  (%i:%02i)" % \
                        (result['artist'] , result['title'],\
                        result['time']/60, result['time']%60 ))
    def clearResults(self):
        self.resultList = []
        self.ui.resultList.clear()

    def _addToPlaylist(self):
        settings = Settings()
        playlistLength = self.parent().server.status()['playlistlength']
        if int(playlistLength) >= int(settings.value("maxPlaylist")):
            return

        row = self.ui.resultList.currentRow()
        try: entry = self.resultList[row]
        except KeyError: return
        self.parent().server.add(entry['file'])

