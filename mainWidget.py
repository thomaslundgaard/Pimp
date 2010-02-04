# -*- coding: utf-8 -*-
from PyQt4 import QtCore,QtGui
from mainWidget_ui import Ui_MainWidget
from helperFunctions import parseTrackInfo
import adminDialog

class MainWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.widgets = (self.ui.stateLabel, self.ui.label_2, self.ui.label_5, \
                self.ui.curTitle, self.ui.curArtist, self.ui.songProgress, \
                self.ui.searchBtn, self.ui.playlist )
        self.onDisconnect()     # setup UI to reflect current status

        # Signals from MPD server
        self.parent().server.sigConnected.connect(self.onConnect)
        self.parent().server.sigDisconnected.connect(self.onDisconnect)
        self.parent().server.sigStatusChanged.connect(self.onStatusChange)

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

    def onStatusChange(self, changeList, status):
        if status['state'] == 'stop' and \
                len(self.parent().server.playlistinfo()) <= 0:
            if self.parent().server.clearFlag:
                self.parent().server.clearFlag = False
            else:
                self.parent().server.addRandomTrack()
                self.parent().server.play()
        if 'time' in changeList:
            self.updateTime(status)
        if 'playlist' in changeList or 'song' in changeList or \
                'state' in changeList:
            self.updateUi(status)

    def updateTime(self, status):
        if status['state'] == 'play' or status['state'] == 'pause':
            elapsed, total = status['time'].split(":")
            elapsed = int(elapsed)
            total = int(total)
            txt = "%d:%02d/%d:%02d" \
                    % (elapsed/60, elapsed%60, total/60, total%60)
            self.ui.songProgress.setValue(elapsed)
            self.ui.songProgress.setMaximum(total)
            self.ui.songProgress.setFormat(txt)
        else:
            self.ui.songProgress.setValue(0)
        timeBeforePlAdd = int(status['xfade']) + 5
        if total-elapsed <= timeBeforePlAdd:
            if len(self.parent().server.playlistinfo()) <= 1:
                self.parent().server.addRandomTrack()

    def updateUi(self, status):
        curSong = parseTrackInfo(self.parent().server.currentsong())
        playlist = self.parent().server.playlistinfo()
        # update labels
        if status['state'] != 'stop':
            if curSong['title']:
                title = curSong['title']
            else: title = "Unknown title"
           
            if curSong['artist']:
                artist = curSong['artist']
            else: artist = "Unknown artist"
            
            self.ui.curTitle.setText(title)
            self.ui.curArtist.setText(artist)
        else:
            self.ui.curTitle.setText ("Not playing")
            self.ui.curArtist.setText ("")
            self.ui.songProgress.setFormat("")
            self.ui.songProgress.setValue(0)
        # update playlist
        self.ui.playlist.clear()
        for song in playlist:
            item = parseTrackInfo(song)
            self.ui.playlist.addItem("%i. %s - %s" \
                    % (item['pos'] + 1 , item['artist'], item['title']))
        # make current track bold
        if curSong['pos'] != None:
            curItem = self.ui.playlist.item(curSong['pos'])
            curItem.setFont (QtGui.QFont("Arial", -1, QtGui.QFont.Bold))
            self.ui.playlist.scrollToItem (curItem, \
                    QtGui.QAbstractItemView.PositionAtCenter)

    def onConnect(self):
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

    def onDisconnect(self):
        for widget in self.widgets:
            widget.setDisabled(True)
        self.ui.curArtist.setText("")
        self.ui.curTitle.setText("Not connected")
        self.ui.playlist.clear()
        self.ui.songProgress.setValue(0)
        self.ui.songProgress.setFormat("")

