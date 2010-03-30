# -*- coding: utf-8 -*-
# PiMP - A mpd-frontend to be used as a jukebox at parties.
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

from PyQt4 import QtCore

class Settings (QtCore.QSettings):
    def __init__ (self):
        QtCore.QSettings.__init__(self)

        self.default = { \
                "adminPassword":		"", \
                "maxPlaylist":			"5", \
                "excludeLongTracks":    "False",\
                "maxTrackLength":       "15",\
                "fullscreenOnStart":    "False", \
                "playOnConnect":        "True", \
                "stopOnQuit":           "True", \
                "mpdServer":	    		"localhost", \
                "mpdPort":		    		"6600", \
                "mpdPassword": 		    "", \
                "vkRow1":               "1234567890", \
                "vkRow2":               "qwertyuiop", \
                "vkRow3":               "asdfghjkl", \
                "vkRow4":               "zxcvbnm"}

    def value (self, key):
        res = QtCore.QSettings.value (self, key, "THIS_KEY_DIDN'T_EXIST")
        if res.toString() == "THIS_KEY_DIDN'T_EXIST":
            return self.default[key]
        else:
            return unicode(res.toString())



