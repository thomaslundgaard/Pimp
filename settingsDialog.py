from PyQt4 import QtCore, QtGui
from settingsDialog_ui import Ui_SettingsDialog
from settings import Settings
from virtualKeyboard import VirtualKeyboard

class SettingsDialog (QtGui.QDialog):
    def __init__ (self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi (self)
        conf = Settings()

        self.ui.pwdEdit.setText (conf.value("adminPassword"))
        self.ui.pwdRepeatEdit.setText (conf.value("adminPassword"))
        self.ui.maxPlaylistSpinBox.setValue (int(conf.value("maxPlaylist")))
        self.ui.mpdServerEdit.setText (conf.value("server"))
        self.ui.mpdPortEdit.setText (conf.value("port"))
        self.ui.mpdPwdEdit.setText (conf.value("password"))
        self.vkb = VirtualKeyboard(self)
        self.vkb.setMinimumSize(600,300)
        self.layout().addWidget(self.vkb)
        QtGui.qApp.focusChanged.connect(self.focusChanged)

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

    def focusChanged(self, old, new):
        if new == self.ui.pwdEdit:
            self.vkb.setInputLine(self.ui.pwdEdit)
        if new == self.ui.pwdRepeatEdit:
            self.vkb.setInputLine(self.ui.pwdRepeatEdit)
        if new == self.ui.maxPlaylistSpinBox:
            self.vkb.setInputLine(self.ui.maxPlaylistSpinBox.lineEdit())
        if new == self.ui.mpdServerEdit:
            self.vkb.setInputLine(self.ui.mpdServerEdit)
        if new == self.ui.mpdPwdEdit:
            self.vkb.setInputLine(self.ui.mpdPwdEdit)
        if new == self.ui.mpdPortEdit:
            self.vkb.setInputLine(self.ui.mpdPortEdit)
