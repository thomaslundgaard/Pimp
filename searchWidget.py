# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from searchWidget_ui import Ui_SearchWidget
from virtualKeyboard import VirtualKeyboard
from settings import Settings
from songItem import SongItem

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
        self.keyWords = [word.lower() for word in words if len(word) >= 2]
        arglist = []
        for word in self.keyWords:
            arglist.extend(["any",word])
        if len(arglist) > 0:
            results = self.parentWidget().server.search(*arglist)
        else:
            results=[]

        self.clearResults()
        for result in results:
            self.resultList.append(SongItem(result))
        self.resultList.sort(self._sortResults, reverse=True)

        for item in self.resultList:
            self.ui.resultList.addItem(unicode(item.textEntry,"utf-8"))
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
        self.parentWidget().server.add(entry.filename)

    def _sortResults(self,x,y):
        #function for sorting SongItems
        #return 1 if x > y
        #return 0 if x = y
        #return -1 if x < y

        if x.artist and y.artist:
            for word in self.keyWords:
                cmpx = x.artist.lower().find(word)
                cmpy = y.artist.lower().find(word)
                if cmpx >= 0 and cmpy >= 0:
                    return cmpy-cmpx
                elif cmpx > cmpy:
                    return 1
                elif cmpx < cmpy:
                    return -1
        
        if x.title and y.title:
            for word in self.keyWords:
                cmpx = x.title.lower().find(word)
                cmpy = y.title.lower().find(word)
                if cmpx >= 0 and cmpy >= 0:
                    return cmpy-cmpx
                if cmpx > cmpy:
                    return 1
                elif cmpx < cmpy:
                    return -1
        if x.title and not y.title:
            return 1
        elif not x.title and y.title:
            return -1
        if x.artist and not y.artist:
            return 1
        elif not x.artist and y.artist:
            return -1
        if not (x.title or x.artist or y.title or y.artist):
            for word in self.keyWords:
                cmpx = x.filename.lower().find(word)
                cmpy = y.filename.lower().find(word)
                if cmpx > cmpy:
                    return 1
                elif cmpx < cmpy:
                    return -1
        return 0


