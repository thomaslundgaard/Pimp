# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from searchWidget_ui import Ui_SearchWidget

class SearchWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_SearchWidget()
        self.ui.setupUi(self)
