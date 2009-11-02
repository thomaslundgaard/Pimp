from PyQt4 import QtCore,QtGui
from mainWindow_ui import Ui_MainWindow
import adminDialog
import mpdclient2
import time

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        self.mpd = mpdclient2.connect()
        self.oldPlaylist = -1
        self.oldSongId = -99	# -1 means not playing
        self.startTimer(250)
        
        self.isFullscreen = False
        #self.showFullScreen()

    def timerEvent(self, event):
        if QtGui.qApp.activeWindow() == None and self.isFullscreen:
            self.showFullScreen()
        if QtGui.qApp.activeWindow() != None and not self.isFullscreen:
            #self.isFullscreen = True
            pass
        self.periodicMpdCheck()

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

    def periodicMpdCheck (self):
        somethingChanged = False
        # See if playlist changed
        if self.oldPlaylist != int (self.mpd.status()['playlist']):
            somethingChanged = True
        # See if song changed
        curSong = self.mpd.currentsong()
        if curSong and int(curSong['id']) != self.oldSongId:
            somethingChanged = True
        elif not curSong and self.oldSongId != -1:
            somethingChanged = True


        if somethingChanged:
            self.ui.playlist.clear()
            for song in self.mpd.playlistinfo():
                self.ui.playlist.addItem( str(int(song['pos'])+1) + '. ' \
                        + song['artist'] + ' - ' + song['title'] )
            self.oldPlaylist = int (self.mpd.status()['playlist'])

            if curSong:
                self.ui.curTitle.setText (curSong['title'])
                self.ui.curArtist.setText (curSong['artist'])
                curItem = self.ui.playlist.item(int(curSong['pos']))
                curItem.setFont (QtGui.QFont("Arial", -1, QtGui.QFont.Bold))
                self.ui.playlist.scrollToItem (curItem, QtGui.QAbstractItemView.PositionAtCenter)
                self.oldSongId = int(curSong['id'])
            else:
                self.ui.curTitle.setText ("Not playing")
                self.ui.curArtist.setText ("")
                self.oldSongId = -1

