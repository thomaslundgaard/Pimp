# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from browseWidget_ui import Ui_browseWidget
from flickcharm import *
from serverInterface import ServerInterfaceError, AddToPlaylistError

class BrowseWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        QtGui.qApp.server.sigDbUpdated.connect(self.updateArtistList)
        QtGui.qApp.server.sigDbUpdated.connect(self.updateGenreTrackLists)
        
        self.ui = Ui_browseWidget()
        self.ui.setupUi(self)
        
        #setup flickcharm
        self.trackCharm = FlickCharm()
        self.trackCharm.activateOn(self.ui.allTrackList)
        self.trackCharm = FlickCharm()
        self.trackCharm.activateOn(self.ui.artistTrackList)
        self.trackCharm = FlickCharm()
        self.trackCharm.activateOn(self.ui.electronicTrackList)
        self.artistCharm = FlickCharm()
        self.artistCharm.activateOn(self.ui.artistList)
        self.genreCharm = FlickCharm()
        self.genreCharm.activateOn(self.ui.genreList)
    
        self.artistList = []
        self.genreList = [[u'All'],\
                          [u'Electronic','trance','dance','house','tech','electro','chiptune','hardstyle'],\
                          [u'Rock','metal','rock','punk','heavy','trash','guitar'],\
                          [u'Pop 70-80-90s','80','70','pop','disco','90'],\
                          [u'Rap / Hip-Hop','rap','hip hop','reggae','gangsta'],\
                         ]
        for genre in self.genreList:
            self.ui.genreList.addItem(genre[0])
        item = self.ui.genreList.item(0)
        item.setFont (QtGui.QFont("Arial", -1, QtGui.QFont.Bold))

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

    def updateGenreTrackLists(self):
        self.ui.allTrackList.clear()
        self.ui.artistTrackList.clear()
        self.ui.electronicTrackList.clear()
        self.ui.rockTrackList.clear()
        self.ui.popTrackList.clear()
        self.ui.rapTrackList.clear()
        
        for genre in self.genreList:
            if genre[0] == u'All':
                cursor = QtGui.qApp.server.trackDB.cursor()
                cursor.execute("select * from tracks order by tag asc")
                for row in cursor:
                    track = {'title':     row[0],\
                        'artist':    row[1],\
                        'file':      row[2],\
                        'time':      row[3],\
                        'tag':       row[4],
                    }
                    item = QtGui.QListWidgetItem("%s - %s  (%i:%02i)" % \
                        (track['artist'] , track['title'],\
                        track['time']/60, track['time']%60 ))
                    item.setData(Qt.UserRole, track['file'])
                    self.ui.allTrackList.addItem(item)
                cursor.close()
            else:
                if genre[0] == u'Electronic':
                    tracklist = self.ui.electronicTrackList
                elif genre[0] == u'Rock':
                    tracklist = self.ui.rockTrackList
                elif genre[0] == u'Pop 70-80-90s':
                    tracklist = self.ui.popTrackList
                elif genre[0] == u'Rap / Hip-Hop':
                    tracklist = self.ui.rapTrackList
                for track in QtGui.qApp.server.searchDBtag(False,*genre[1:-1]):
                    item = QtGui.QListWidgetItem("%s - %s  (%i:%02i)" % \
                        (track['artist'] , track['title'],\
                        track['time']/60, track['time']%60 ))
                    item.setData(Qt.UserRole, track['file'])
                    tracklist.addItem(item)

    def updateArtistList(self):
        self.ui.artistList.clear()
        self.artistList = []

        cursor = QtGui.qApp.server.trackDB.cursor()
        cursor.execute("select artist from tracks order by artist asc")
        count = 1
        prevArtist = -1
        for artist in cursor:
            if artist[0] != prevArtist and prevArtist >= 0:
                self.artistList.append(prevArtist)
                self.ui.artistList.addItem("%s (%i)" % (prevArtist, count))
                count = 1
            else:
                count += 1
            prevArtist = artist[0]
        self.artistList.append(prevArtist)
        self.ui.artistList.addItem("%s (%i)" % (prevArtist, count))

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
        self.ui.artistTrackList.clear()
        self.ui.trackStackedWidget.setCurrentWidget(self.ui.artist)
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
            self.ui.artistTrackList.addItem("%s (%i:%02i)" % \
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
        
        if genre[0] == u'All':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.all)
            self.ui.allTrackList.clearSelection()
        if genre[0] == u'Electronic':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.electronic)
            self.ui.electronicTrackList.clearSelection()
        elif genre[0] == u'Rock':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.rock)
            self.ui.rockTrackList.clearSelection()
        elif genre[0] == u'Pop 70-80-90s':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.pop)
            self.ui.popTrackList.clearSelection()
        elif genre[0] == u'Rap / Hip-Hop':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.rap)
            self.ui.rapTrackList.clearSelection()


    def _addToPlaylist(self):
        curWid = self.ui.trackStackedWidget.currentWidget()
        if curWid == self.ui.all:
            tracklist = self.ui.allTrackList
        elif curWid == self.ui.artist:
            tracklist = self.ui.artistTrackList
        elif curWid == self.ui.electronic:
            tracklist = self.ui.electronicTrackList
        elif curWid == self.ui.rock:
            tracklist = self.ui.rockTrackList
        elif curWid == self.ui.pop:
            tracklist = self.ui.popTrackList
        elif curWid == self.ui.rap:
            tracklist = self.ui.rapTrackList
        else:
            return False
        
        if len(tracklist.selectedItems()) < 1:
            return False

        item = tracklist.currentItem()
        file = unicode(item.data(Qt.UserRole).toString().toUtf8(), 'utf-8')
        text = unicode(item.text().toUtf8(), 'utf-8')

        try:
            answer = QtGui.qApp.server.addToPlaylist(file)
            self.ui.infoLabel.setText("Added %s" % (text) )
            self.ui.infoLabel.show()
            return True
        except ServerInterfaceError:
            return False
        except AddToPlaylistError as inst:
            self.ui.infoLabel.setText(inst.args[0])
            self.ui.infoLabel.show()
            return False

    def clearSelection(self):
        self.ui.genreList.setCurrentRow(0)
        self.ui.infoLabel.hide()
