from PyQt4 import QtCore


class Settings (QtCore.QSettings):
    def __init__ (self):
        QtCore.QSettings.__init__(self)

        self.default = { \
                "adminPassword":		"hidden", \
                "maxPlaylist":			"5", \
                "mpdServer":			"localhost", \
                "mpdPort":				"", \
                "mpdPwd":				"" }

    def value (self, key):
        res = QtCore.QSettings.value (self, key, "THIS_KEY_DIDN'T_EXIST")
        if res.toString() == "THIS_KEY_DIDN'T_EXIST":
            return self.default[key]
        else:
            return res.toString()



