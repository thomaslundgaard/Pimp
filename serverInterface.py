# -*- coding: utf-8 -*-

## Documentation ##
# Signals:
#   connected()

from PyQt4 import QtCore
from settings import Settings
from mpd import *
import socket


class ServerInterface(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.settings = Settings()
        self.mpd = MPDClient()
        self.connect()

    def timerEvent(self, event):
        self.emit(QtCore.SIGNAL("songChanged"))

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

        self.emit(QtCore.SIGNAL("connected()"))
        self.startTimer(250)
        return True

