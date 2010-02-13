# -*- coding: utf-8 -*-
import random
import socket
import sqlite3
import time
from datetime import datetime

from PyQt4 import QtCore, QtGui
from mpd import *

from settings import Settings
from dbUpdate import *
from helperFunctions import *

class ServerInterfaceError(Exception):
    def __init__(self):
        Exception.__init__(self)

class AddToPlaylistError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class ServerInterface(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigDbUpdated = QtCore.pyqtSignal()
    sigStatusChanged = QtCore.pyqtSignal(list,dict)     # changeList, mpdStatus

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.client = MPDClient()
        self.settings = Settings()
        self.mpdServer = str(self.settings.value("mpdServer"))
        self.mpdPort = str(self.settings.value("mpdPort"))
        self.mpdPassword = str(self.settings.value("mpdPassword"))

        self.lastState=-9999
        self.lastSongid=-9999
        self.lastTime=-9999
        self.lastPlaylist=-9999
        self.connected = False
        self.shuffleList = []
        self.timerId = False
        self.autoAdd = True
        self.trackDB = None 
        self.sigConnected.connect(self._onConnected)
        self.sigStatusChanged.connect(self._onStatusChanged)
        QtGui.qApp.aboutToQuit.connect(self._onAppQuit)

    def connect(self):
        try:
            self.client.connect(host=self.mpdServer, port=self.mpdPort)
        except socket.error:
            print datetime.now().isoformat(" ") + \
            ": Unable to connect to MPD: Socket error (will try again in 2 sec)"
            QtCore.QTimer.singleShot(2000, self.connect)
            return
        if self.mpdPassword != "":
            try:
                self.client.password(self.mpdPassword)
            except CommandError:
                print datetime.now().isoformat(" ") + \
                        ": Unable to connect to MPD: Invalid password"
                return
        if not self.trackDB:    # this is the first connection
            self.dbUpdate()
        else:
            self.connected = True
            self.sigConnected.emit()
            
    def dbUpdate(self):
        self.trackDB = sqlite3.connect(':memory:')
        self.dbUpdateDialog = DbUpdateDialog()
        self.dbUpdateDialog.ui.mpdupdatePixmap.show()
        self.dbUpdateDialog.setModal(True)
        self.dbUpdateDialog.show()
        self.dbUpdateWorker = DbUpdateWorker(self.client)
        self.dbUpdateWorker.sigRemoteUpdateFinished.connect( \
                self.onRemoteUpdateFinished)
        self.dbUpdateWorker.sigDbDownloaded.connect(self.onDbDownloaded)
        self.dbUpdateWorker.sigDbUpdateFailed.connect(self.onDbUpdateFailed)
        self.dbUpdateWorker.start()

    def onRemoteUpdateFinished(self):
        self.dbUpdateDialog.ui.mpdupdatePixmap.setEnabled(True)
        self.dbUpdateDialog.ui.sqlupdatePixmap.show()

    def onDbUpdateFailed(self):
        self.trackDB = None
        self.dbUpdateDialog.accept()
        self._lostConnection()

    def onDbDownloaded(self, tracks):
        cursor = self.trackDB.cursor()
        cursor.execute("drop table if exists tracks")
        cursor.execute('''create table if not exists tracks
        (title text, artist text, file text, time integer, tag text)
        ''')
        for t in tracks:
            cursor.execute('''insert into tracks(title, artist, file, 
            time, tag) values( ?, ?, ?, ?, ?) ''',\
            (t['title'], t['artist'], t['file'], t['time'], t['tag'])
            )
        self.trackDB.commit()
        cursor.close()
        self.dbUpdateDialog.ui.sqlupdatePixmap.setEnabled(True)
        self.dbUpdateDialog.accept()
        self.connected = True
        self.sigConnected.emit()
        self.sigDbUpdated.emit()

    def play(self):
        if not self.connected:
            raise ServerInterfaceError()
        if int(self.status()['playlistlength']) == 0:
            self.addRandomTrack()
        try:
            return self.client.play()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def pause(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.pause()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def stop(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.stop()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def playPause(self):
        if self.status()['state'] == 'play':
            return self.pause()
        else:
            return self.play()

    def next(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.next()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def add(self, filename):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.add(filename.encode("utf-8"))
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def clear(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.clear()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def status(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.status()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def currentsong(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.currentsong()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def playlistinfo(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.playlistinfo()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def listall(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.listall()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def listallinfo(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.listallinfo()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def deleteid(self, id):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.deleteid(id)
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def update(self):
        if not self.connected:
            raise ServerInterfaceError()
        try:
            return self.client.update()
        except (socket.error, ConnectionError):
            self._lostConnection()
            raise ServerInterfaceError()

    def clearExceptCurrent(self):
        try:
            playlist = self.playlistinfo()
            status = self.status()
            if status['state'] == "play":
                for item in playlist:
                    if item['id'] != status['songid']:
                        self.deleteid(item['id'])
            else:
                self.autoAdd = False
                self.clear()    # clear completely if not playing
        except ServerInterfaceError:
            pass

    def addToPlaylist(self, filename):
        for item in self.playlistinfo():
            if parseTrackInfo(item)['file'] == filename:
                raise AddToPlaylistError("Track already in playlist!")
        playlistLength = int(self.status()['playlistlength'])
        if playlistLength >= int(self.settings.value("maxPlaylist")):
            raise AddToPlaylistError("Playlist full!")
        else:
            self.add(filename)
            self.play()

    def addRandomTrack(self):
        if len(self.shuffleList) <= 0:
            cursor = self.trackDB.cursor()
            cursor.execute("select file from tracks")
            self.shuffleList = [item[0] for item in cursor]
            cursor.close()
            random.shuffle(self.shuffleList)

        if self.shuffleList: # shuffleList can be empty if no tracks in mpd db
            self.add(self.shuffleList.pop())

    def searchDBtag(self, anded, *argwords):
        keywords = [ '%' + word + '%' for word in argwords]
        if anded: lop = 'and'
        else: lop='or'
        cursor = self.trackDB.cursor()
        query = """ select * from tracks where tag like ?"""
        for i in range(len(keywords) - 1):
            query += " %s tag like ?" % lop

        query += " order by tag asc"

        cursor.execute(query, tuple(keywords))
        for row in cursor:
            yield {'title':     row[0],\
                   'artist':    row[1],\
                   'file':      row[2],\
                   'time':      row[3],\
                   'tag':       row[4],
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

    def _onAppQuit(self):
        if self.settings.value("stopOnQuit") == "True":
            try:
                self.stop()
            except ServerInterfaceError:
                pass

    def _onStatusChanged(self, changeList, status):
        if not self.autoAdd:
            self.autoAdd = True
            return
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
        self.timerId = self.startTimer(400)
        try:
            self.client.random(0)
            self.client.repeat(1)
            try:
                self.client.single(0)
                self.client.consume(1)
            except AttributeError:
                # Ugly hack: python-mpd doesn't support these commands (yet),
                # so we just add them
                self.client._commands["consume"] = self.client._commands["play"]
                self.client._commands["single"] = self.client._commands["play"]
                self.client.single(0)
                self.client.consume(1)
        except (socket.error, ConnectionError):
            self._lostConnection()
            return
        self.play()

    def _lostConnection(self):
        print datetime.now().isoformat(" ") + \
                ": Lost connection to MPD. Trying to reconnect..."
        if self.timerId:
            self.killTimer(self.timerId)
            self. timerId = False
        self.lastState = -9999
        self.lastSong = -9999
        self.lastTime = -9999
        self.lastPlaylist = -9999
        self.connected = False
        self.sigDisconnected.emit()
        self.client.disconnect()
        self.connect()

