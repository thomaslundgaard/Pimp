# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from settings import Settings
from mpd import *
from helperFunctions import *
import random
import socket
import sqlite3
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
        self.trackDB = sqlite3.connect(':memory:')
        self.clearFlag = False
        self.shuffleList = []

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
        self.updateDB()
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

    def updateDB(self):
        tracklist = [track for track in self.listallinfo() if 'file' in track]
        tracks = map(parseTrackInfo,tracklist)
        cursor = self.trackDB.cursor()
        cursor.execute('''create table tracks
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

    def clearExceptCurrent(self):
        playlist = self.playlistinfo()
        try:
            curId = self.status()['songid']
        except KeyError:
            print "key error"
            self.clearFlag = True
            self.clear()
            return
        for item in playlist:
            if item['id'] != curId:
                self.deleteid(item['id'])

    def addToPlaylist(self, filename):
        for item in self.playlistinfo():
            if parseTrackInfo(item)['file'] == filename:
                return "alreadyInPlaylist"
        playlistLength = int(self.status()['playlistlength'])
        if playlistLength >= int(self.settings.value("maxPlaylist")):
            return "playlistFull"
        else:
            self.add(filename)
            return "added"

    def addRandomTrack(self):
        if len(self.shuffleList) <= 0:
            self._createShuffleList()
        self.add(self.shuffleList.pop())
        
    def _createShuffleList(self):
        self.shuffleList = [dict['file'] for dict \
                in self.listall() if 'file' in dict]
        random.shuffle(self.shuffleList)

