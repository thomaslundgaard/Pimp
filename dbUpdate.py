import time
from PyQt4 import QtGui, QtCore
from dbUpdateDialog_ui import Ui_DbUpdateDialog
from helperFunctions import *
import socket
from mpd import ConnectionError

class DbUpdateDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_DbUpdateDialog()
        self.ui.setupUi(self)
        self.ui.mpdupdatePixmap.hide()
        self.ui.sqlupdatePixmap.hide()

    def reject(self):
        pass

class DbUpdateWorker(QtCore.QThread):
    sigRemoteUpdateFinished = QtCore.pyqtSignal()
    sigDbDownloaded = QtCore.pyqtSignal(list)   # list with tracks
    sigDbUpdateFailed = QtCore.pyqtSignal()

    def __init__(self, mpdClient):
        QtCore.QThread.__init__(self)
        self.mpdClient = mpdClient

    def run(self):
        try:
            jobID = self.mpdClient.update()
            while True:
                time.sleep(0.4)
                stat = self.mpdClient.status()
                if not ('updating_db' in stat and stat['updating_db'] == jobID):
                    break
            self.sigRemoteUpdateFinished.emit()

            tracklist = [track for track in self.mpdClient.listallinfo() \
                    if 'file' in track]
            tracks = map(parseTrackInfo,tracklist)
            self.sigDbDownloaded.emit(tracks)
        except (socket.error, ConnectionError):
            self.sigDbUpdateFailed.emit()

