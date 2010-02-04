# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from adminDialog_ui import Ui_AdminDialog
from virtualKeyboard import VirtualKeyboard
import settingsDialog
from settings import Settings

class AdminDialog(QtGui.QDialog):
    def __init__ (self,  parent = None):
        QtGui.QDialog.__init__ (self,  parent)
        self.ui = Ui_AdminDialog ()
        self.ui.setupUi (self)
        self.ui.infoLabel.hide()
        # Hack to update playPauseBtn
        self.onServerStatusChange(['state'], \
                self.parent().parent().server.status() )
        self.ui.pwdEdit.setFocus()
        vkb = VirtualKeyboard(self,self.ui.pwdEdit)
        vkb.setMinimumSize(600,300)
        self.layout().addWidget(vkb)
        self.resize(-1, -1)
        self.parent().parent().server.sigStatusChanged.connect( \
                self.onServerStatusChange)
    
    def checkPwd(self):
        settings = Settings()
        if self.ui.pwdEdit.text() == settings.value("adminPassword"):
            return True
        else:
           self.ui.pwdEdit.clear()
           self.ui.infoLabel.setText("Invalid password - please try again:")
           self.ui.infoLabel.show()
           self.ui.pwdEdit.setFocus()
           return False

    def leaveFullscreen(self):
        if self.checkPwd():
            self.parent().parent().leaveFullscreen()
            self.close()

    def playPause(self):
        if self.checkPwd():
            if self.parent().parent().server.status()['state'] == 'play':
                self.parent().parent().server.pause()
            else:
                self.parent().parent().server.play()

    def onServerStatusChange(self, changeList, status):
        if 'state' in changeList:
            if status['state'] == 'play':
                self.ui.playPauseBtn.setText("Pause &playback")
            else:
                self.ui.playPauseBtn.setText("Start &playback")

    def nextTrack(self):
        if self.checkPwd():
            self.parent().parent().server.next()

    def clearPlaylist(self):
        # Clears playlist, except currently playing track
        if self.checkPwd():
            self.parent().parent().server.clearExceptCurrent()

    def settings (self):
        if self.checkPwd():
            dialog = settingsDialog.SettingsDialog(self)
            dialog.exec_()
            self.close()
        
    def quitApp(self):
        if self.checkPwd():
            QtGui.qApp.quit()
            self.close()

    def cancelDialog(self):
        self.close()
