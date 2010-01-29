# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from settings import Settings
from mpd import *
import socket

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
        self.connect()

    def connect(self):
        server = self.settings.value("server")
        port = self.settings.value("port")
        password = self.settings.value("password")
        try:
            MPDClient.connect (self, host=server, port=port)
        except socket.error:
            print "Unable to connect to MPD: Socket error (I will try again in 2 sec)"
            QtCore.QTimer.singleShot(2000, self.connect )
            return False
        if password != "":
            try:
                self.password(password)
            except CommandError:
                print "Unable to connect to MPD: Invalid password"
                return False
        self.sigConnected.emit()
        self.startTimer(500)
        return True

    def timerEvent(self, event):
        try:
            status = self.status()
        except socket.error:
            print "Lost connection to MPD. Trying to reconnect"
            self.sigDisconnected.emit()
            self.stopTimer()
            self.disconnect()
            self.connect()
            return
        if status['playlist'] != self.lastPlaylist or \
         status['songid'] != self.lastSong:
            self.sigPlaylistChanged.emit(int(status['playlist']))
            self.lastPlaylist = status['playlist']
        if status['songid'] != self.lastSong:
            self.sigSongChanged.emit(int(status['songid']))
            self.lastSong = status['songid']
        if 'time' in status and status['time'] != self.lastTime:
            elapsed, total = status['time'].split(":")
            self.sigTimeChanged.emit(int(elapsed), int(total))
            self.lastTime = status['time']
        if status['state'] != self.lastState:
            self.sigStateChanged.emit(status['state'])
            self.lastState = status['state']

