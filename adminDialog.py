from PyQt4 import QtGui, QtCore
from adminDialog_ui import Ui_AdminDialog

class AdminDialog(QtGui.QDialog):
    def __init__ (self,  parent = None):
        QtGui.QDialog.__init__ (self,  parent)
        self.ui = Ui_AdminDialog ()
        self.ui.setupUi (self)
        self.ui.pwdEdit.setFocus()
        
