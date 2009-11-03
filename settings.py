from PyQt4 import QtCore


class Settings (QtCore.QSettings):
    def __init__ (self):
        QtCore.QSettings.__init__(self)

        self.default = { \
                "adminPassword":		"hidden", \
                "maxPlaylist":			"5" }

    def value (self, key):
        res = QtCore.QSettings.value (self, key)
        if res.toString() == '':
            return self.default[key]
        else:
            return res.toString()



