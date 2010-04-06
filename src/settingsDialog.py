# -*- coding: utf-8 -*-
# Pimp - A mpd-frontend to be used as a jukebox at parties.
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
        self.ui.maxTrackLengthSpinBox.setValue( \
                int(conf.value("maxTrackLength")))
        self.ui.mpdServerEdit.setText (conf.value("mpdServer"))
        self.ui.mpdPortEdit.setText (conf.value("mpdPort"))
        self.ui.mpdPasswordEdit.setText (conf.value("mpdPassword"))
        if( conf.value("fullscreenOnStart") == "True" ):
            self.ui.fullscreenOnStartCheckBox.setChecked(True)
        else:
            self.ui.fullscreenOnStartCheckBox.setChecked(False)
        if( conf.value("playOnConnect") == "True" ):
            self.ui.playOnConnectCheckBox.setChecked(True)
        else:
            self.ui.playOnConnectCheckBox.setChecked(False)
        if( conf.value("stopOnQuit") == "True" ):
            self.ui.stopOnQuitCheckBox.setChecked(True)
        else:
            self.ui.stopOnQuitCheckBox.setChecked(False)
        if (conf.value("excludeLongTracks") == "True"):
            self.ui.excludeLongTracksCheckbox.setChecked(True)
            self.ui.maxTrackLengthSpinBox.setEnabled(True)
            self.ui.maxTrackLengthLabel.setEnabled(True)
            self.ui.maxTrackLengthUp.setEnabled(True)
            self.ui.maxTrackLengthDown.setEnabled(True)
        else:
            self.ui.excludeLongTracksCheckbox.setChecked(False)
            self.ui.maxTrackLengthSpinBox.setEnabled(False)
            self.ui.maxTrackLengthLabel.setEnabled(False)
            self.ui.maxTrackLengthUp.setEnabled(False)
            self.ui.maxTrackLengthDown.setEnabled(False)
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
        conf.setValue ("maxTrackLength", self.ui.maxTrackLengthSpinBox.value() )
        if self.ui.excludeLongTracksCheckbox.isChecked():
            conf.setValue("excludeLongTracks", "True")
        else:
            conf.setValue("excludeLongTracks", "False")
        if self.ui.fullscreenOnStartCheckBox.isChecked():
            conf.setValue("fullscreenOnStart", "True" )
        else:
            conf.setValue("fullscreenOnStart", "False" )
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
        if new == self.ui.maxTrackLengthSpinBox:
            self.vkb.setInputLine(self.ui.maxTrackLengthSpinBox.lineEdit())
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
    
    def tabChanged(self, newtab):
        self.vkb.setInputLine(None)
        #Sets focus to the widget, that last had focus
        #when the new tab was left. This makes vkb edit the right lineEdit.
        lastfocusWidget = newtab.focusWidget()
        newtab.clearFocus()
        if lastfocusWidget: #Could be None
            lastfocusWidget.setFocus()

