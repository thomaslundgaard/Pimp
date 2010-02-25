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
        self.ui.sqlupdatePixmap.setPixmap( \
                QtGui.QPixmap(QtGui.qApp.pixmapsPath + "/tick.svg"))
        self.ui.mpdupdatePixmap.setPixmap( \
                QtGui.QPixmap(QtGui.qApp.pixmapsPath + "/tick.svg"))

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

