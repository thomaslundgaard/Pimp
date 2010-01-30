# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore,QtGui
from mainWindow import MainWindow

def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("res/karaoke.png"))
    app.setOrganizationName("Blupix");
    app.setApplicationName("PyMpdJuke");

    app.setStyleSheet("\
            * { \
                background: qlineargradient(spread:pad, x1:1, y1:1, x2:1,\
                    y2:0, stop:0.565217 rgba(50, 50, 50, 255), \
                    stop:1 rgba(100, 100, 100, 255)); \
                font: 14pt \"Sans Serif\"; \
                color: rgb(237, 237, 237);\
            }\
            QLineEdit {\
                border-style: groove;\
                border-width: 1px;\
                border-color: grey;\
            }\
            QSpinBox {\
                border-style: groove;\
                border-width: 1px;\
                border-color: grey;\
            }\
            \
            QScrollBar:vertical {\
                width:50px;\
                margin: 50px 0px 50px 0px;\
            } \
            QScrollbar::handle:vertical {\
                min-height:40px;\
            }\
            QScrollBar::add-line:vertical {\
                height: 50px; \
                border: 2px solid grey;\
                subcontrol-position: bottom;\
                subcontrol-origin: margin;\
            }\
            QScrollBar::sub-line:vertical {\
                    height: 50px;\
                    border: 2px solid grey;\
                    subcontrol-position: top;\
                    subcontrol-origin: margin;\
            }\
            QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {\
                width: 3px;\
                height: 3px;\
                background:white;\
            }\
            \
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\
                background: none;\
            }\
            ")    
    #QtCore.Qt.setOrganizationDomain("mysoft.com");
    window = MainWindow()
    window.setWindowTitle("PyMPDJuke")
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
 
