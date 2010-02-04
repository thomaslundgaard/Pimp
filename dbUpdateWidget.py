from PyQt4 import QtGui
from dbUpdateWidget_ui import Ui_DbUpdateWidget

class DbUpdateWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_DbUpdateWidget()
        self.ui.setupUi(self)
        self.ui.mpdupdatePixmap.hide()
        self.ui.sqlupdatePixmap.hide()
