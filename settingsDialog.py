from PyQt4 import QtCore, QtGui
from settingsDialog_ui import Ui_SettingsDialog
from settings import Settings


class SettingsDialog (QtGui.QDialog):
    def __init__ (self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi (self)

        conf = Settings()
        self.ui.pwdEdit.setText (conf.value("adminPassword"))
        self.ui.pwdRepeatEdit.setText (conf.value("adminPassword"))
        self.ui.maxPlaylistSpinBox.setValue (int(conf.value("maxPlaylist")))

    def okBtn (self):
        if self.ui.pwdEdit.text() != self.ui.pwdRepeatEdit.text():
            mb = QtGui.QMessageBox ("Admin passwords not the same", \
                    "The two new admin passwords you entered, are not the same", \
                    QtGui.QMessageBox.NoIcon, QtGui.QMessageBox.Ok, \
                    QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton, \
                    self )
            mb.exec_()
            return
        conf = Settings()
        conf.setValue ("adminPassword", self.ui.pwdEdit.text())
        conf.setValue ("maxPlaylist", self.ui.maxPlaylistSpinBox.value() )
        self.close()

    def cancelBtn (self):
        self.close()

