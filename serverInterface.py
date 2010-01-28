# -*- coding: utf-8 -*-

## Documentation ##
# Signals:
#   connected()

from PyQt4 import QtCore
from settings import Settings
from mpd import *
import socket


class ServerInterface(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigSongChanged = QtCore.pyqtSignal()
    sigTimeChanged = QtCore.pyqtSignal()
    sigPlaylistChanged = QtCore.pyqtSignal()
    sigStateChanged = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.lastState=-23
        self.settings = Settings()
        self.mpd = MPDClient()
        self.connect()

    def connect(self):
        server = self.settings.value("server")
        port = self.settings.value("port")
        password = self.settings.value("password")
        try:
            self.mpd.connect (host=server, port=port)
        except socket.error:
            print "Unable to connect: Socket error (I will try again in 2 sec)"
            QtCore.QTimer.singleShot(2000, self.connect )
            return False
        if password != "":
            try:
                self.mpd.password(password)
            except CommandError:
                print "Unable to connect: Invalid password"
                return False
        self.sigConnected.emit()
        self.startTimer(250)
        return True

    def timerEvent(self, event):
        status = self.mpd.status()
        if status['state'] != self.lastState:
            self.sigStateChanged.emit()
            self.lastState = status['state']
