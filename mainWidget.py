# -*- coding: utf-8 -*-
from PyQt4 import QtCore,QtGui
from mainWidget_ui import Ui_MainWidget
import adminDialog

class MainWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.widgets = (self.ui.stateLabel, self.ui.label_2, self.ui.label_5, \
                self.ui.curTitle, self.ui.curArtist, self.ui.songProgress, \
                self.ui.searchBtn, self.ui.playlist )
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

    def songChanged(self, songId):
        if self.parent().server.status()['state'] != 'stop':
            curSong = self.parent().server.currentsong()
            self.ui.curTitle.setText (unicode(curSong['title'],"utf8"))
            self.ui.curArtist.setText (unicode(curSong['artist'],"utf8"))
            curItem = self.ui.playlist.item(int(curSong['pos']))
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
        for song in self.parent().server.playlistinfo():
            self.ui.playlist.addItem( str(int(song['pos'])+1) + '. ' \
                    + unicode(song['artist'],"utf8") + ' - ' \
                    + unicode(song['title'],"utf8") )

    def connected(self):
        for widget in self.widgets:
            widget.setDisabled(False)
        self.ui.curTitle.setText("Not playing")

    def disconnected(self):
        for widget in self.widgets:
            widget.setDisabled(True)
        self.ui.curArtist.setText("")
        self.ui.curTitle.setText("Not connected")
        self.ui.playlist.clear()
        self.ui.songProgress.setValue(0)
        self.ui.songProgress.setFormat("")

