# -*- coding: utf-8 -*-
from PyQt4 import QtCore,QtGui
from mainWidget_ui import Ui_MainWidget
from serverInterface import ServerInterface
import adminDialog

class MainWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)

        #Set UI styles TODO:Setting progressbar color doesnt work
        #tmppalette = self.ui.songProgress.palette()
        #tmppalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("red"))
        #tmppalette.setColor(QtGui.QPalette.Foreground, QtGui.QColor("red"))
        #self.ui.songProgress.setPalette(tmppalette)

        self.isFullscreen = False
        #self.showFullScreen()

        # Server & callbacks
        self.server = ServerInterface()
        self.server.sigStateChanged.connect(self.stateChanged)
        self.server.sigSongChanged.connect(self.songChanged)
        self.server.sigTimeChanged.connect(self.timeChanged)
        self.server.sigPlaylistChanged.connect(self.playlistChanged)

    def timerEvent(self, event):
        if QtGui.qApp.activeWindow() == None and self.isFullscreen:
            self.showFullScreen()
        if QtGui.qApp.activeWindow() != None and not self.isFullscreen:
            #self.isFullscreen = True
            pass

    def closeEvent(self, event):
        if self.isFullscreen:
            QtCore.QEvent.ignore(event)

    def enterAdmin(self):
        if self.isFullscreen:
            dialog = adminDialog.AdminDialog(self)
            dialog.exec_()
        else:
            self.isFullscreen = True
            self.showFullScreen()

    def enterSearch(self):
        self.parent.gotoSearchWidget()

    def stateChanged(self, state):
        if state == 'stop':
            self.ui.curTitle.setText ("Not playing")
            self.ui.curArtist.setText ("")

    def songChanged(self, songId):
        if self.server.status()['state'] != 'stop':
            curSong = self.server.currentsong()
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
        for song in self.server.playlistinfo():
            self.ui.playlist.addItem( str(int(song['pos'])+1) + '. ' \
                    + unicode(song['artist'],"utf8") + ' - ' \
                    + unicode(song['title'],"utf8") )

