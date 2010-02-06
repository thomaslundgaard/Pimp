# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from settings import Settings

class VirtualKeyboard(QtGui.QWidget):
    def __init__(self, parent=None, inputField=None):
        QtGui.QWidget.__init__(self, parent)
        self.inputField = inputField
        grid = QtGui.QGridLayout()
        grid.setSpacing(1)

        settings = Settings()

        row1String = settings.value("vkRow1")
        row2String = settings.value("vkRow2")
        row3String = settings.value("vkRow3")
        row4String = settings.value("vkRow4")
        maxButtons = max([len(row1String), len(row2String), \
                len(row3String), len(row4String)])
        
        for i, s in enumerate(row1String):
            button = keyboardPushbutton(s.upper())
            button.clicked.connect(button._onClicked)
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            button.setMinimumSize(5,5)
            grid.addWidget(button, 0, 4*i, 1, 4)


        for i, s  in enumerate(row2String):
            button = keyboardPushbutton(s.upper())
            button.clicked.connect(button._onClicked)
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            button.setMinimumSize(5,5)
            grid.addWidget(button, 1, 4*i + 1, 1, 4)

        for i, s in enumerate(row3String):
            button = keyboardPushbutton(s.upper())
            button.clicked.connect(button._onClicked)
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            button.setMinimumSize(5,5)
            grid.addWidget(button, 2, 4*i + 2, 1, 4)

        for i, s in enumerate(row4String):
            button = keyboardPushbutton(s.upper())
            button.clicked.connect(button._onClicked)
            button.sigClicked.connect(self._onCharKeyDown) 
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                    QtGui.QSizePolicy.Expanding)
            button.setMinimumSize(5,5)
            grid.addWidget(button, 3, 4*i + 3, 1, 4)

        backspaceButton = QtGui.QPushButton("Back")
        backspaceButton.clicked.connect(self._onBackspaceDown)
        backspaceButton.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                QtGui.QSizePolicy.Expanding)
        backspaceButton.setMinimumSize(5,5)
        grid.addWidget(backspaceButton, 3, len(row4String)*4 + 3, 1, 4)

        clearButton = QtGui.QPushButton("Clear")
        clearButton.clicked.connect(self._onClearDown)
        clearButton.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                QtGui.QSizePolicy.Expanding)
        clearButton.setMinimumSize(5,5)
        grid.addWidget(clearButton, 3, (len(row4String)+ 1)*4 + 3, 1, 4)

        columns = grid.columnCount()
        spaceButton = keyboardPushbutton(" ")
        spaceButton.clicked.connect(spaceButton._onClicked)
        spaceButton.sigClicked.connect(self._onCharKeyDown)
        spaceButton.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                QtGui.QSizePolicy.Expanding)
        spaceButton.setMinimumSize(5,5)
        grid.addWidget(spaceButton,4,columns/6,1,columns - columns/3)

        self.setLayout(grid)

    def setInputLine(self, lineEdit):
        self.inputField = lineEdit

    def _onCharKeyDown(self, char):
        try: self.inputField.insert(char)
        except AttributeError: pass

    def _onBackspaceDown(self):
        try: self.inputField.backspace()
        except AttributeError: pass

    def _onClearDown(self):
        try: self.inputField.clear()
        except AttributeError: pass
        

class keyboardPushbutton(QtGui.QPushButton):
    sigClicked = QtCore.pyqtSignal(str)
    def __init__(self, *args, **keywords):
        QtGui.QPushButton.__init__(self, *args, **keywords)
    def _onClicked(self):
        self.sigClicked.emit(str(self.text()).lower())


