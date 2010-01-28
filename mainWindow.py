from PyQt4 import QtCore,QtGui
from mainWindow_ui import Ui_MainWindow
from serverInterface import ServerInterface
import adminDialog
import mpdclient2
import time

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = ServerInterface()

        #Set UI styles TODO:Setting progressbar color doesnt work
        tmppalette = self.ui.songProgress.palette()
        tmppalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("red"))
        tmppalette.setColor(QtGui.QPalette.Foreground, QtGui.QColor("red"))
        self.ui.songProgress.setPalette(tmppalette)

        self.mpd = mpdclient2.connect()
        self.oldPlaylistId = -1
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
        if self.oldPlaylistId != int (self.mpd.status()['playlist']):
            somethingChanged = True
        # See if play status or song changed
        if self.mpd.status()['state'] == "play":
            if self.oldSongId == -1:
                somethingChanged = True
            if int (self.mpd.currentsong()['id']) != self.oldSongId:
                somethingChanged = True
        else:
            if self.oldSongId != -1:
                somethingChanged = True

        if somethingChanged:
            self.ui.playlist.clear()
            for song in self.mpd.playlistinfo():
                self.ui.playlist.addItem( str(int(song['pos'])+1) + '. ' \
                        + unicode(song['artist'],"utf8") + ' - ' \
                        + unicode(song['title'],"utf8") )
            self.oldPlaylistId = int (self.mpd.status()['playlist'])

            if self.mpd.status()['state'] == "play":
                curSong = self.mpd.currentsong()
                self.ui.curTitle.setText (unicode(curSong['title'],"utf8"))
                self.ui.curArtist.setText (unicode(curSong['artist'],"utf8"))
                curItem = self.ui.playlist.item(int(curSong['pos']))
                curItem.setFont (QtGui.QFont("Arial", -1, QtGui.QFont.Bold))
                self.ui.playlist.scrollToItem (curItem, \
                        QtGui.QAbstractItemView.PositionAtCenter)
                self.oldSongId = int(curSong['id'])
            else:
                self.ui.curTitle.setText ("Not playing")
                self.ui.curArtist.setText ("")
                self.oldSongId = -1

        #Always update progress bar
        try: 
            timestr = self.mpd.status()['time']
        except KeyError:
            timestr = "-1:-1"
        now, length = timestr.split(":")
        now = str( int(now)/60 ) + ":" + str(int(now)%60)
        length = str( int(length)/60 ) + ":" + str(int(length)%60)
