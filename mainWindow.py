from PyQt4 import QtCore,QtGui
from mainWindow_ui import Ui_MainWindow
import mpdclient2

# This is a hack, to capture if the window loses focus (fx by alt-tab)
# and if so, make the window stay fullscreen and not lose focus
class EventFilter(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ActivationChange:
            if not obj.recentlyMinimized:
                obj.isFullscreen = True
                obj.showFullScreen()
            obj.recentlyMinimized = False
        return QtCore.QObject.eventFilter(self, obj, event)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.installEventFilter(EventFilter(self))

        self.mpd = mpdclient2.connect()
        self.showFullScreen()
        self.isFullscreen = True
        self.recentlyMinimized = False
        self.startTimer(250)

    def timerEvent(self, event):
        self.updateUi()

    def closeEvent(self, event):
        if self.isFullscreen:
            QtCore.QEvent.ignore(event)

    def updateUi (self):
        songInfo = self.mpd.currentsong()
        if songInfo:
            self.ui.curTitle.setText (songInfo['title'])
            #self.ui.curArtist.setText (songInfo['artist'])
        else:
            self.ui.curTitle.setText ("Not playing")
            self.ui.curArtist.setText ("Not playing")

        currentSong = self.mpd.currentsong().pos
        self.ui.playlist.clear()
        for song in self.mpd.playlistinfo():
            self.ui.playlist.addItem( str(int(song['pos'])+1) + '. ' + song['title'] )
            if song['pos'] == currentSong:
                self.ui.playlist.item(int(song['pos'])).setFont (QtGui.QFont("Arial", -1, QtGui.QFont.Bold))

    def enterAdmin(self):
        if self.isFullscreen:
            self.isFullscreen = False
            self.recentlyMinimized = True
            self.showNormal()
            self.showMinimized()
        else:
            self.isFullscreen = True
            self.showFullScreen()

