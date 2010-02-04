# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from settings import Settings
from mpd import *
from helperFunctions import *
from dbUpdateWidget import DbUpdateWidget
import socket
import sqlite3
import time
from datetime import datetime

class ServerInterface(QtCore.QObject, MPDClient):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigStatusChanged = QtCore.pyqtSignal(list,dict)     # changeList, mpdStatus

    def __init__(self):
        QtCore.QObject.__init__(self)
        MPDClient.__init__(self)
        self.settings = Settings()
        self.lastState=-9999
        self.lastSongid=-9999
        self.lastTime=-9999
        self.lastPlaylist=-9999
        self.sigConnected.connect(self._onConnect)
        self.trackDB = None 

    def connect(self):
        server = str(self.settings.value("mpdServer"))
        port = str(self.settings.value("mpdPort"))
        password = str(self.settings.value("mpdPassword"))
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
        changeList = []
        try:
            status = self.status()
        except socket.error:
            self.disconnected()
            return
        except ConnectionError:
            self.disconnected()
            return
        if status['playlist'] != self.lastPlaylist:
            changeList.append('playlist')
            self.lastPlaylist = status['playlist']
        if 'songid' in status and status['songid'] != self.lastSongid:
            changeList.append('song')
            self.lastSongid = status['songid']
        if 'time' in status and status['time'] != self.lastTime:
            changeList.append('time')
            self.lastTime = status['time']
        if status['state'] != self.lastState:
            changeList.append('state')
            self.lastState = status['state']
        self.sigStatusChanged.emit(changeList, status)

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

    def _onConnect(self):
        if not self.trackDB:
            self.trackDB = sqlite3.connect(':memory:')

    def updateDBs(self):
        dialog = DbUpdateWidget()
        dialog.ui.mpdupdatePixmap.show()
        dialog.show()
        jobID = self.update()
        app = QtGui.qApp
        while True:
            time.sleep(0.1)
            app.processEvents()
            stat = self.status()
            if not ('updating_db' in stat and stat['updating_db'] == jobID):
                break
        dialog.ui.mpdupdatePixmap.setEnabled(True)
        dialog.ui.sqlupdatePixmap.show()
        app.processEvents()
        app.processEvents()
        tracklist = [track for track in self.listallinfo() if 'file' in track]
        tracks = map(parseTrackInfo,tracklist)
        cursor = self.trackDB.cursor()
        cursor.execute("drop table if exists tracks")
        cursor.execute('''create table if not exists tracks
        (title text, artist text, file text, album text,
        genre text, time integer, pos integer, tag text)
        ''')
        for t in tracks:
            cursor.execute('''insert into tracks(title, artist, file, album, 
            genre, time, pos, tag) values( ?, ?, ?, ?, ?, ?, ?, ?) ''',\
            (t['title'], t['artist'], t['file'], t['album'], t['genre'], t['time'],\
            t['pos'], t['tag'])
            )
        self.trackDB.commit()
        cursor.close()
        dialog.ui.sqlupdatePixmap.setEnabled(True)
        app.processEvents()
        app.processEvents()
        time.sleep(1)

    def searchDB(self,keywords):
        keywords = [ '%' + word + '%' for word in keywords]
        cursor = self.trackDB.cursor()
        query = """ select * from tracks where tag like ?"""
        for i in range(len(keywords) - 1):
            query += """ and tag like ?"""

        query += " order by tag asc"

        cursor.execute(query, tuple(keywords))
        for row in cursor:
            yield {'title':     row[0],\
                   'artist':    row[1],\
                   'file':      row[2],\
                   'album':     row[3],\
                   'genre':     row[4],\
                   'time':      row[5],\
                   'pos':       row[6],\
                   'tag':       row[7],
                }
        cursor.close()
