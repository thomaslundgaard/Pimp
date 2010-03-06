# -*- coding: utf-8 -*-
# PyMpdJuke - A mpd-frontend to be used as a jukebox at parties.
# Copyright (C) 2010 Peter Bjørn
# Copyright (C) 2010 Thomas Lundgaard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        self.artistTrackCharm = FlickCharm()
        self.artistTrackCharm.activateOn(self.ui.artistTrackList)
        self.electronicCharm = FlickCharm()
        self.electronicCharm.activateOn(self.ui.electronicTrackList)
        self.rockCharm = FlickCharm()
        self.rockCharm.activateOn(self.ui.rockTrackList)
        self.popCharm = FlickCharm()
        self.popCharm.activateOn(self.ui.popTrackList)
        self.rapCharm = FlickCharm()
        self.rapCharm.activateOn(self.ui.rapTrackList)

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
                    QtGui.qApp.processEvents()
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
                    QtGui.qApp.processEvents()
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
            QtGui.qApp.processEvents()
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
        cursor = QtGui.qApp.server.trackDB.cursor()
        cursor.execute(''' select * from tracks where artist == ?
                order by title asc''', (artist,))
        for row in cursor:
            #track = {'title':     row[0],\
                   #'artist':    row[1],\
                   #'file':      row[2],\
                   #'time':      row[3],\
                   #'tag':       row[4],
            #}
            item = QtGui.QListWidgetItem("%s - %s  (%i:%02i)" % \
                (row[1] , row[0],\
                row[3]/60, row[3]%60 ))
            item.setData(Qt.UserRole, row[2])
            self.ui.artistTrackList.addItem(item)
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
            self.ui.allTrackList.scrollToTop()
        if genre[0] == u'Electronic':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.electronic)
            self.ui.electronicTrackList.clearSelection()
            self.ui.electronicTrackList.scrollToTop()
        elif genre[0] == u'Rock':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.rock)
            self.ui.rockTrackList.clearSelection()
            self.ui.rockTrackList.scrollToTop()
        elif genre[0] == u'Pop 70-80-90s':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.pop)
            self.ui.popTrackList.clearSelection()
            self.ui.popTrackList.scrollToTop()
        elif genre[0] == u'Rap / Hip-Hop':
            self.ui.trackStackedWidget.setCurrentWidget(self.ui.rap)
            self.ui.rapTrackList.clearSelection()
            self.ui.rapTrackList.scrollToTop()


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
        self.ui.artistList.scrollToTop()
        self.ui.genreList.scrollToTop()
        self.ui.allTrackList.scrollToTop()
        self.ui.infoLabel.hide()
