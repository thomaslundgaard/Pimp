# -*- coding: utf-8 -*-
from PyQt4 import QtCore,QtGui
from mainWidget_ui import Ui_MainWidget
from helperFunctions import parseTrackInfo
import adminDialog
from flickcharm import *

class MainWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.charm = FlickCharm()
        self.charm.activateOn(self.ui.playlist)
        self.widgets = (self.ui.stateLabel, self.ui.label_2, self.ui.label_5, \
                self.ui.curTitle, self.ui.curArtist, self.ui.songProgress, \
                self.ui.searchBtn, self.ui.playlist )
        # setup UI to reflect current status
        if QtGui.qApp.server.connected:
            self.onServerConnected()
        else:
            self.onServerDisconnected()
        # Signals from MPD server
        QtGui.qApp.server.sigConnected.connect(self.onServerConnected)
        QtGui.qApp.server.sigDisconnected.connect(self.onServerDisconnected)
        QtGui.qApp.server.sigStatusChanged.connect(self.onServerStatusChanged)

    def enterAdmin(self):
        dialog = adminDialog.AdminDialog(self)
        dialog.exec_()

    def enterSearch(self):
        self.parent().gotoSearchWidget()

    def enterBrowse(self):
        self.parent().gotoBrowseWidget()

    def enterFullscreen(self):
        if self.parent().isFullscreen:
            self.enterAdmin()
        else:
            self.parent().gotoFullscreen()

    def onServerConnected(self):
        for widget in self.widgets:
            widget.setDisabled(False)
        self.ui.curTitle.setText("Not playing")

    def onServerDisconnected(self):
        for widget in self.widgets:
            widget.setDisabled(True)
        self.ui.curArtist.setText("")
        self.ui.curTitle.setText("Not connected")
        self.ui.playlist.clear()
        self.ui.songProgress.setValue(0)
        self.ui.songProgress.setFormat("")

    def onServerStatusChanged(self, changeList, status):
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

    def updateUi(self, status):
        try:
            curSong = parseTrackInfo(QtGui.qApp.server.currentsong())
            playlist = QtGui.qApp.server.playlistinfo()
        except ServerInterfaceError:
            return
        # update labels
        if status['state'] != 'stop':
            self.ui.curTitle.setText(curSong['title'])
            self.ui.curArtist.setText(curSong['artist'])
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

