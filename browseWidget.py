# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from browseWidget_ui import Ui_browseWidget
from flickcharm import *
from serverInterface import ServerInterfaceError, AddToPlaylistError

class BrowseWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        QtGui.qApp.server.sigDbUpdated.connect(self.updateArtistList)
        
        self.ui = Ui_browseWidget()
        self.ui.setupUi(self)
        
        #setup flickcharm
        self.trackCharm = FlickCharm()
        self.trackCharm.activateOn(self.ui.trackList)
        self.artistCharm = FlickCharm()
        self.artistCharm.activateOn(self.ui.artistList)
        self.genreCharm = FlickCharm()
        self.genreCharm.activateOn(self.ui.genreList)
    
        self.artistList = []
        self.genreList = [[u'Electronic','trance','dance','house','tech','electro','chiptune','hardstyle'],\
                          [u'Rock','metal','rock','punk','heavy','trash','guitar'],\
                          [u'Pop 70-80-90s','80','70','pop','disco','90'],\
                          [u'Rap / Hip-Hop','rap','hip hop','reggae','gangsta'],\
                         ]
        for genre in self.genreList:
            self.ui.genreList.addItem(genre[0])
        self.trackList = []
    def addContinue(self):
        self._addToPlaylist()

    def addClose(self):
        if self._addToPlaylist():
            self.cancel()

    def switchToSearch(self):
        self.parent().gotoSearchWidget()

    def cancel(self):
        self.parent().gotoMainWidget()

    def updateArtistList(self):
        self.ui.artistList.clear()
        self.artistList = []
        cursor = QtGui.qApp.server.trackDB.cursor()
        cursor.execute("select distinct artist from tracks asc")
        artists = cursor.fetchall()
        for artist in artists:
            cursor.execute("select count(*) from tracks \
                    where artist == ?",artist)
            count = cursor.fetchall()[0][0]
            self.ui.artistList.addItem("%s (%i)" % (artist[0], count))
            self.artistList.append(artist[0])
            
        cursor.close()

    def onArtistChanged(self):
        if len(self.ui.artistList.selectedItems()) > 0:
            self.ui.genreList.clearSelection()
        else:
            return

        try:
            artist = self.artistList[self.ui.artistList.currentRow()]
        except IndexError:
            return
        self.ui.trackList.clear()
        self.trackList = []
        cursor = QtGui.qApp.server.trackDB.cursor()
        cursor.execute(''' select * from tracks where artist == ?
                order by title asc''', (artist,))
        for row in cursor:
            dict = {'title':     row[0],\
                   'artist':    row[1],\
                   'file':      row[2],\
                   'time':      row[3],\
                   'tag':       row[4],
            }
            self.ui.trackList.addItem("%s (%i:%02i)" % \
                (dict['title'],dict['time']/60, dict['time']%60 ))
            self.trackList.append(dict)
        cursor.close()

    def onGenreChanged(self):
        if len(self.ui.genreList.selectedItems()) > 0:
            self.ui.artistList.clearSelection()
        else:
            return

        try:
            genre = self.genreList[self.ui.genreList.currentRow()]
        except IndexError:
            return
        self.ui.trackList.clear()
        self.trackList = []
        for track in QtGui.qApp.server.searchDBtag(False,*genre[1:-1]):
            self.trackList.append(track)
            self.ui.trackList.addItem("%s - %s  (%i:%02i)" % \
                    (track['artist'] , track['title'],\
                    track['time']/60, track['time']%60 ))

    def _addToPlaylist(self):
        row = self.ui.trackList.currentRow()
        if row < 0:
            return False
        try:
            entry = self.trackList[row]
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
