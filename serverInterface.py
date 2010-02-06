# -*- coding: utf-8 -*-
import random
import socket
import sqlite3
import time
from datetime import datetime

from PyQt4 import QtCore, QtGui
from mpd import *

from settings import Settings
from dbUpdateWidget import DbUpdateWidget
from helperFunctions import *

class ServerInterfaceError(Exception):
    pass

class ServerInterface(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigStatusChanged = QtCore.pyqtSignal(list,dict)     # changeList, mpdStatus

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.server = MPDClient()
        self.settings = Settings()
        self.lastState=-9999
        self.lastSongid=-9999
        self.lastTime=-9999
        self.lastPlaylist=-9999
        self.connected = False
        self.shuffleList = []
        self.trackDB = None 
        self.sigConnected.connect(self._onConnected)
        self.sigStatusChanged.connect(self._onStatusChanged)

    def connect(self):
        server = str(self.settings.value("mpdServer"))
        port = str(self.settings.value("mpdPort"))
        password = str(self.settings.value("mpdPassword"))
        try:
            self.server.connect(host=server, port=port)
        except socket.error:
            print datetime.now().isoformat(" ") + \
            ": Unable to connect to MPD: Socket error (will try again in 2 sec)"
            QtCore.QTimer.singleShot(2000, self.connect)
            raise ServerInterfaceError()
        if password != "":
            try:
                self.server.password(password)
            except CommandError:
                print datetime.now().isoformat(" ") + \
                        ": Unable to connect to MPD: Invalid password"
                raise ServerInterfaceError()
        self.connected = True
        self.sigConnected.emit()
        self.timerId = self.startTimer(400)
        return

    def play(self):
        if not self.connected:
            raise ServerInterfaceError()
        if int(self.status()['playlistlength']) == 0:
            self.addRandomTrack()
        try:
            return self.server.play()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def playPause(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            if self.server.status()['state'] == 'play':
                return self.server.pause()
            else:
                return self.play()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def next(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.next()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def add(self, filename):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.add(filename)
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def status(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.status()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def currentsong(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.currentsong()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def playlistinfo(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.playlistinfo()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def listall(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.listall()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def listallinfo(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.listallinfo()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def deleteid(self, id):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.deleteid(id)
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def update(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.server.update()
        except socket.error:
            self._lostConnection()
            raise ServerInterfaceError()
        except ConnectionError:
            self._lostConnection()
            raise ServerInterfaceError()

    def clearExceptCurrent(self):
        playlist = self.playlistinfo()
        try:
            curId = self.status()['songid']
        except KeyError:
            self.clear()    # clear completely if not playing
        for item in playlist:
            if item['id'] != curId:
                self.server.deleteid(item['id'])

    def addToPlaylist(self, filename):
        for item in self.playlistinfo():
            if parseTrackInfo(item)['file'] == filename:
                return "alreadyInPlaylist"
        playlistLength = int(self.status()['playlistlength'])
        if playlistLength >= int(self.settings.value("maxPlaylist")):
            return "playlistFull"
        else:
            self.add(filename.encode("utf-8"))
            self.play()
            return "added"

    def addRandomTrack(self):
        if len(self.shuffleList) <= 0:
            self.shuffleList = \
                [dict['file'] for dict in self.listall() if 'file' in dict]
            random.shuffle(self.shuffleList)
        self.add(self.shuffleList.pop())

    def updateDBs(self):
        dialog = DbUpdateWidget()
        dialog.ui.mpdupdatePixmap.show()
        try:
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
        except ServerInterfaceError:
            return

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

    def timerEvent(self, event):
        changeList = []
        try:
            status = self.status()
        except ServerInterfaceError:
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
        if changeList:
            self.sigStatusChanged.emit(changeList, status)

    def _onStatusChanged(self, changeList, status):
        if 'state' in changeList and status['state'] == 'stop' and \
                int(status['playlistlength']) == 0:
            self.play()     # play() adds random track
        if 'time' in changeList:
            timeBeforePlAdd = int(status['xfade']) + 2
            elapsed, total = status['time'].split(":")
            elapsed = int(elapsed)
            total = int(total)
            if total-elapsed<=timeBeforePlAdd and \
                    int(status['playlistlength'])<=1:
                self.addRandomTrack()

    def _onConnected(self):
        if not self.trackDB:
            self.trackDB = sqlite3.connect(':memory:')

        try:
            self.server.random(0)
            self.server.repeat(1)
            try:
                self.server.single(0)
            except AttributeError:
                print "Can't deactivate single mode automatically"
            try:
                self.server.consume(1)
            except AttributeError:
                print "Can't activate consume mode automatically"
        except socket.error:
            self._lostConnection()
            return
        except ConnectionError:
            self._lostConnection()
            return
        self.play()

    def _lostConnection(self):
        print datetime.now().isoformat(" ") + \
                ": Lost connection to MPD. Trying to reconnect..."
        self.lastState = -9999
        self.lastSong = -9999
        self.lastTime = -9999
        self.lastPlaylist = -9999
        self.connected = False
        self.sigDisconnected.emit()
        self.killTimer(self.timerId)
        MPDClient.disconnect(self.server)
        self.connect()

