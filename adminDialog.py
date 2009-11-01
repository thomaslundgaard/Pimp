from PyQt4 import QtGui, QtCore
from adminDialog_ui import Ui_AdminDialog

class AdminDialog(QtGui.QDialog):
    def __init__ (self,  parent = None):
        QtGui.QDialog.__init__ (self,  parent)
        self.ui = Ui_AdminDialog ()
        self.ui.setupUi (self)
        self.ui.pwdEdit.setFocus()
    
    def checkPwd(self):
        if str(self.ui.pwdEdit.text()) == "kkk":
            return True
        else:
            return False

    def minimizeApp(self):
        if self.checkPwd():
            self.parent().isFullscreen = False
            self.parent().showMinimized()
        self.close()
        
    def quitApp(self):
        print "quitting?"
        if self.checkPwd():
            self.parent().close()

    def cancelDialog(self):
        self.close()
