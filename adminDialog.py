from PyQt4 import QtGui, QtCore
from adminDialog_ui import Ui_AdminDialog

class AdminDialog(QtGui.QDialog):
    def __init__ (self,  parent = None):
        QtGui.QDialog.__init__ (self,  parent)
        self.ui = Ui_AdminDialog ()
        self.ui.setupUi (self)
        self.ui.infoLabel.hide()
        self.resize(-1, -1)
        self.ui.pwdEdit.setFocus()
    
    def checkPwd(self):
         if self.ui.pwdEdit.text() == "kkk":
            return True
         else:
            self.ui.pwdEdit.clear()
            self.ui.infoLabel.setText("Invalid password - please try again:")
            self.ui.infoLabel.show()
            self.ui.pwdEdit.setFocus()
            return False

    def minimizeApp(self):
        if self.checkPwd():
            self.parent().isFullscreen = False
            self.parent().showMinimized()
            self.close()
        
    def quitApp(self):
        if self.checkPwd():
            QtGui.qApp.quit()
            self.close()

    def cancelDialog(self):
        self.close()

