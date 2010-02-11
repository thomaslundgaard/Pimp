# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from adminDialog_ui import Ui_AdminDialog
from virtualKeyboard import VirtualKeyboard
import settingsDialog
from settings import Settings
from serverInterface import ServerInterfaceError

class AdminDialog(QtGui.QDialog):
    def __init__ (self,  parent = None):
        QtGui.QDialog.__init__ (self,  parent)
        self.ui = Ui_AdminDialog ()
        self.ui.setupUi (self)
        self.ui.infoLabel.hide()
        self.ui.pwdEdit.setFocus()
        vkb = VirtualKeyboard(self,self.ui.pwdEdit)
        vkb.setMinimumSize(600,300)
        self.layout().addWidget(vkb)
        # update playPauseBtn
        if QtGui.qApp.server.connected:
            self.onServerConnected()
        else:
            self.onServerDisconnected()
        try:
            self.onServerStatusChanged(['state'], QtGui.qApp.server.status())
        except ServerInterfaceError:
            pass
        QtGui.qApp.server.sigStatusChanged.connect( \
                self.onServerStatusChanged)
        QtGui.qApp.server.sigConnected.connect( \
                self.onServerConnected)
        QtGui.qApp.server.sigDisconnected.connect( \
                self.onServerDisconnected)
        self.resize(-1, -1)
    
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
            try:
                QtGui.qApp.server.playPause()
            except ServerInterfaceError:
                return

    def onServerStatusChanged(self, changeList, status):
        if 'state' in changeList:
            if status['state'] == 'play':
                self.ui.playPauseBtn.setText("Pause &playback")
            else:
                self.ui.playPauseBtn.setText("Start &playback")
                
    def onServerConnected(self):
        self.ui.playPauseBtn.setEnabled(True)
        self.ui.nextBtn.setEnabled(True)
        self.ui.clearBtn.setEnabled(True)

    def onServerDisconnected(self):
        self.ui.playPauseBtn.setEnabled(False)
        self.ui.nextBtn.setEnabled(False)
        self.ui.clearBtn.setEnabled(False)

    def nextTrack(self):
        if self.checkPwd():
            try:
                QtGui.qApp.server.next()
            except ServerInterfaceError:
                return

    def clearPlaylist(self):
        # Clears playlist, except currently playing track
        if self.checkPwd():
            try:
                QtGui.qApp.server.clearExceptCurrent()
            except ServerInterfaceError:
                return

    def settings (self):
        if self.checkPwd():
            dialog = settingsDialog.SettingsDialog(self)
            dialog.exec_()
        
    def quitApp(self):
        if self.checkPwd():
            QtGui.qApp.quit()
            self.close()

    def cancelDialog(self):
        self.close()
