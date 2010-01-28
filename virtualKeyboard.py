from PyQt4 import QtCore, QtGui
from settings import Settings

class virtualKeyboard(QtGui.QtWidget):
    def __init__(self, parent=None, inputField=None):
        self.inputField = inputField
        QtGui.QtWidget.__init__(self, parent)
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        hbox3 = QtGui.QHBoxLayout()
        hbox4 = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)

        settings = Settings()

        row1String = settings.value("vkRow1")
        
        for s in row1String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            hbox1.addWidget(button)
        for s in row2String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            hbox2.addWidget(button)
        for s in row3String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            hbox3.addWidget(button)
        for s in row4String:
            button = keyboardPushbutton(s.upper())
            button.sigClicked.connect(self._onCharKeyDown) 
            hbox4.addWidget(button)

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


