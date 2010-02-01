# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from settings import Settings
from mpd import *
import socket
from datetime import datetime

class ServerInterface(QtCore.QObject, MPDClient):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigStateChanged = QtCore.pyqtSignal(str)
    sigSongChanged = QtCore.pyqtSignal(int)
    sigTimeChanged = QtCore.pyqtSignal(int,int)     # (elapsed, total)
    sigPlaylistChanged = QtCore.pyqtSignal(int)

    def __init__(self):
        QtCore.QObject.__init__(self)
        MPDClient.__init__(self)
        self.settings = Settings()
        self.lastState=-9999
        self.lastSong=-9999
        self.lastTime=-9999
        self.lastPlaylist=-9999

    def connect(self):
        server = self.settings.value("mpdServer")
        port = self.settings.value("mpdPort")
        password = self.settings.value("mpdPassword")
        try:
            MPDClient.connect (self, host=server, port=port)
        except socket.error:
            print datetime.now().isoformat(" ") + \
            ": Unable to connect to MPD: Socket error (will try again in 2 sec)"
            QtCore.QTimer.singleShot(2000, self.connect )
            return False
        if password != "":
            try:
                self.password(password)
            except CommandError:
                print datetime.now().isoformat(" ") + \
                        ": Unable to connect to MPD: Invalid password"
                return False
        self.sigConnected.emit()
        self.timerId = self.startTimer(400)
        return True

    def timerEvent(self, event):
        try:
            status = self.status()
        except socket.error:
            self.disconnected()
            return
        except ConnectionError:
            self.disconnected()
            return
        if status['playlist'] != self.lastPlaylist or \
         'songid' in status and status['songid'] != self.lastSong:
            self.sigPlaylistChanged.emit(int(status['playlist']))
            self.lastPlaylist = status['playlist']
        if 'songid' in status and status['songid'] != self.lastSong:
            self.sigSongChanged.emit(int(status['songid']))
            self.lastSong = status['songid']
        if 'time' in status and status['time'] != self.lastTime:
            elapsed, total = status['time'].split(":")
            self.sigTimeChanged.emit(int(elapsed), int(total))
            self.lastTime = status['time']
        if status['state'] != self.lastState:
            self.sigStateChanged.emit(status['state'])
            self.lastState = status['state']

    def disconnected(self):
        print datetime.now().isoformat(" ") + \
                ": Lost connection to MPD. Trying to reconnect..."
        self.lastState=-9999
        self.lastSong=-9999
        self.lastTime=-9999
        self.lastPlaylist=-9999
        self.sigDisconnected.emit()
        self.killTimer(self.timerId)
        MPDClient.disconnect(self)
        self.connect()
