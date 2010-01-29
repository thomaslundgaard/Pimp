from PyQt4 import QtCore, QtGui
from settings import Settings

class VirtualKeyboard(QtGui.QWidget):
    def __init__(self, parent=None, inputField=None):
        QtGui.QWidget.__init__(self, parent)
        self.inputField = inputField
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        hbox3 = QtGui.QHBoxLayout()
        hbox4 = QtGui.QHBoxLayout()

        settings = Settings()

        row1String = settings.value("vkRow1")
        row2String = settings.value("vkRow2")
        row3String = settings.value("vkRow3")
        row4String = settings.value("vkRow4")
        maxButtons = max([len(row1String), len(row2String), \
                len(row3String), len(row4String)])
        
        for s in row1String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            hbox1.addWidget(button)
        for i in range(maxButtons - len(row1String)): 
            button = keyboardPushbutton(" ")
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            hbox1.addWidget(button)

        for s in row2String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            hbox2.addWidget(button)
        for i in range(maxButtons - len(row2String)): 
            button = keyboardPushbutton(" ")
            button.setVisible=False
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            hbox2.addWidget(button)

        for s in row3String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            hbox3.addWidget(button)
        for i in range(maxButtons - len(row3String)): 
            spacer = QtGui.QSpacerItem(1,1)
            #button.hide()
            #button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
            #        QtGui.QSizePolicy.Expanding)
            hbox3.addStretch(0)

        for s in row4String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            hbox4.addWidget(button)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        
        spaceButton = keyboardPushbutton(" ")
        spaceButton.sigClicked.connect(self._onCharKeyDown)
        spaceButton.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                QtGui.QSizePolicy.Expanding)
        vbox.addWidget(spaceButton)

        self.setLayout(vbox)

    def setInputField(self, lineEdit):
        self.inputField = lineEdit

    def _onCharKeyDown(self, char):
        self.inputField.insert(char)
        

class keyboardPushbutton(QtGui.QPushButton):
    sigClicked = QtCore.pyqtSignal(str)
    def __init__(self, *args, **keywords):
        QtGui.QPushButton.__init__(self, *args, **keywords)
    def _onClicked(self):
        self.sigClicked.emit(self.text)


