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
        self.resize(-1, -1)
        self.ui.pwdEdit.setFocus()
        vkb = VirtualKeyboard(self,self.ui.pwdEdit)
        vkb.setMinimumSize(320,240)
        self.layout().addWidget(vkb)
    
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

    def minimizeApp(self):
        if self.checkPwd():
            self.parent().parent().leaveFullscreen()
            self.close()
        
    def quitApp(self):
        if self.checkPwd():
            QtGui.qApp.quit()
            self.close()

    def cancelDialog(self):
        self.close()

    def settings (self):
        if self.checkPwd():
            dialog = settingsDialog.SettingsDialog(self)
            dialog.exec_()
            self.close()
