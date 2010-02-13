# -*- coding: utf-8 -*-
from PyQt4 import QtCore

class Settings (QtCore.QSettings):
    def __init__ (self):
        QtCore.QSettings.__init__(self)

        self.default = { \
                "adminPassword":		"hidden", \
                "maxPlaylist":			"5", \
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
            return res.toString()



