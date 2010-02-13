# -*- coding: utf-8 -*-
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

        self.ui.adminPasswordEdit.setText (conf.value("adminPassword"))
        self.ui.adminPasswordRepeatEdit.setText (conf.value("adminPassword"))
        self.ui.maxPlaylistSpinBox.setValue (int(conf.value("maxPlaylist")))
        self.ui.mpdServerEdit.setText (conf.value("mpdServer"))
        self.ui.mpdPortEdit.setText (conf.value("mpdPort"))
        self.ui.mpdPasswordEdit.setText (conf.value("mpdPassword"))
        if( conf.value("playOnConnect") == "True" ):
            self.ui.playOnConnectCheckBox.setChecked(True)
        else:
            self.ui.playOnConnectCheckBox.setChecked(False)
        if( conf.value("stopOnQuit") == "True" ):
            self.ui.stopOnQuitCheckBox.setChecked(True)
        else:
            self.ui.stopOnQuitCheckBox.setChecked(False)
        self.ui.vkRow1Edit.setText (conf.value("vkRow1"))
        self.ui.vkRow2Edit.setText (conf.value("vkRow2"))
        self.ui.vkRow3Edit.setText (conf.value("vkRow3"))
        self.ui.vkRow4Edit.setText (conf.value("vkRow4"))

        self.vkb = VirtualKeyboard(self)
        self.vkb.setMinimumSize(600,300)
        self.layout().addWidget(self.vkb)
        QtGui.qApp.focusChanged.connect(self.focusChanged)

    def okBtn (self):
        if self.ui.adminPasswordEdit.text() != self.ui.adminPasswordRepeatEdit.text():
            mb = QtGui.QMessageBox ("Admin passwords not the same", \
                    "The two new admin passwords you entered, are not the same", \
                    QtGui.QMessageBox.NoIcon, QtGui.QMessageBox.Ok, \
                    QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton, \
                    self )
            mb.exec_()
            return
        conf = Settings()
        conf.setValue ("adminPassword", self.ui.adminPasswordEdit.text())
        conf.setValue ("maxPlaylist", self.ui.maxPlaylistSpinBox.value() )
        if self.ui.playOnConnectCheckBox.isChecked():
            conf.setValue("playOnConnect", "True" )
        else:
            conf.setValue("playOnConnect", "False" )
        if self.ui.stopOnQuitCheckBox.isChecked():
            conf.setValue("stopOnQuit", "True" )
        else:
            conf.setValue("stopOnQuit", "False" )
        conf.setValue ("vkRow1", self.ui.vkRow1Edit.text() )
        conf.setValue ("vkRow2", self.ui.vkRow2Edit.text() )
        conf.setValue ("vkRow3", self.ui.vkRow3Edit.text() )
        conf.setValue ("vkRow4", self.ui.vkRow4Edit.text() )
        conf.setValue ("mpdServer", self.ui.mpdServerEdit.text() )
        conf.setValue ("mpdPort", self.ui.mpdPortEdit.text() )
        conf.setValue ("mpdPassword", self.ui.mpdPasswordEdit.text() )
        self.close()

    def cancelBtn (self):
        self.close()

    def focusChanged(self, old, new):
        if new == self.ui.adminPasswordEdit:
            self.vkb.setInputLine(self.ui.adminPasswordEdit)
        if new == self.ui.adminPasswordRepeatEdit:
            self.vkb.setInputLine(self.ui.adminPasswordRepeatEdit)
        if new == self.ui.maxPlaylistSpinBox:
            self.vkb.setInputLine(self.ui.maxPlaylistSpinBox.lineEdit())
        if new == self.ui.mpdServerEdit:
            self.vkb.setInputLine(self.ui.mpdServerEdit)
        if new == self.ui.mpdPasswordEdit:
            self.vkb.setInputLine(self.ui.mpdPasswordEdit)
        if new == self.ui.mpdPortEdit:
            self.vkb.setInputLine(self.ui.mpdPortEdit)
        if new == self.ui.vkRow1Edit:
            self.vkb.setInputLine(self.ui.vkRow1Edit)
        if new == self.ui.vkRow2Edit:
            self.vkb.setInputLine(self.ui.vkRow2Edit)
        if new == self.ui.vkRow3Edit:
            self.vkb.setInputLine(self.ui.vkRow3Edit)
        if new == self.ui.vkRow4Edit:
            self.vkb.setInputLine(self.ui.vkRow4Edit)

