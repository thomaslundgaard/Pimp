# -*- coding: utf-8 -*-
from PyQt4 import QtCore,QtGui
import random
from mainWidget_ui import Ui_MainWidget
from songItem import SongItem
import adminDialog

class MainWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.widgets = (self.ui.stateLabel, self.ui.label_2, self.ui.label_5, \
                self.ui.curTitle, self.ui.curArtist, self.ui.songProgress, \
                self.ui.searchBtn, self.ui.playlist )
        self.shuffleList = []
        self.disconnected()     # setup UI to reflect current status

        # Signals from MPD server
        self.parent().server.sigConnected.connect(self.connected)
        self.parent().server.sigDisconnected.connect(self.disconnected)
        self.parent().server.sigStateChanged.connect(self.stateChanged)
        self.parent().server.sigSongChanged.connect(self.songChanged)
        self.parent().server.sigTimeChanged.connect(self.timeChanged)
        self.parent().server.sigPlaylistChanged.connect(self.playlistChanged)

    def enterAdmin(self):
        dialog = adminDialog.AdminDialog(self)
        dialog.exec_()

    def enterSearch(self):
        self.parent().gotoSearchWidget()

    def enterFullscreen(self):
        if self.parent().isFullscreen:
            self.enterAdmin()
        else:
            self.parent().gotoFullscreen()

    def stateChanged(self, state):
        if state == 'stop':
            self.ui.curTitle.setText ("Not playing")
            self.ui.curArtist.setText ("")
            self.ui.songProgress.setFormat("")
            self.ui.songProgress.setValue(0)
        elif state == "play":
            self.songChanged(0) #update artist and title labels

    def songChanged(self, songId):
        if self.parent().server.status()['state'] != 'stop':
            curSong = SongItem(self.parent().server.currentsong())
            if curSong.title or curSong.artist:
                if curSong.title:
                    title = curSong.title
                else: title = "Unknown title"
                if curSong.artist:
                    artist = curSong.artist
                else: artist = "Unknown artist"
                    #self.ui.curTitle.setText (unicode(curSong.title,"utf8"))
            else:
                title = curSong.filename.split('/').pop().split('-').pop().split('.')[0:-1]
                title = "".join(title).strip()
                artist = curSong.filename.split('/').pop().split('-').pop(0).split('.')[0:-1]
                artist = "".join(artist).strip()

            self.ui.curTitle.setText(unicode(title,"utf8"))
            self.ui.curArtist.setText(unicode(artist,"utf8"))

            curItem = self.ui.playlist.item(curSong.pos)
            curItem.setFont (QtGui.QFont("Arial", -1, QtGui.QFont.Bold))
            self.ui.playlist.scrollToItem (curItem, \
                    QtGui.QAbstractItemView.PositionAtCenter)

    def timeChanged(self, elapsed, total):
        txt = "%d:%02d/%d:%02d" % (elapsed/60, elapsed%60, total/60, total%60)
        self.ui.songProgress.setValue (elapsed)
        self.ui.songProgress.setMaximum (total)
        self.ui.songProgress.setFormat(txt)

    def playlistChanged(self, playlistId):
        self.ui.playlist.clear()
        playlist = self.parent().server.playlistinfo()
        for song in playlist:
            item = SongItem(song)
            self.ui.playlist.addItem( unicode( \
                    "%i. %s" % (item.pos + 1, item.textEntry),"utf8"))
        self.songChanged(0) #hack to remark the playing song
        if len(playlist) <= 0:
            if len(self.shuffleList) <= 0:
                self.createShuffleList()
            self.parent().server.add(self.shuffleList.pop())
            self.parent().server.play()

    def connected(self):
        for widget in self.widgets:
            widget.setDisabled(False)
        self.ui.curTitle.setText("Not playing")
        status = self.parent().server.status()
        self.parent().server.random(0)
        self.parent().server.repeat(1)
        try:
            self.parent().server.single(0)
        except AttributeError:
            print "Can't deactivate single mode automatically"
        try:
            self.parent().server.consume(1)
        except AttributeError:
            print "Can't activate consume mode automatically"
        self.parent().server.play()
    def createShuffleList(self):
        self.shuffleList = [dict['file'] for dict \
                in self.parent().server.listall() if 'file' in dict]
        random.shuffle(self.shuffleList)

    def disconnected(self):
        for widget in self.widgets:
            widget.setDisabled(True)
        self.ui.curArtist.setText("")
        self.ui.curTitle.setText("Not connected")
        self.ui.playlist.clear()
        self.ui.songProgress.setValue(0)
        self.ui.songProgress.setFormat("")

