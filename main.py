# I used  this code to test layouts

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget,QHBoxLayout,QGridLayout,QStackedLayout,QPushButton,QToolBar
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QSize
from scripts.pages_classes import *
class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)



        
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        #window settings
        min_width=1200
        min_height=600
        self.setWindowTitle("My Analisys_App")
        self.setMinimumSize(min_width, min_height)

        #toolbar definition

        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(16,16)) # important for icons! Otherwise padding makes them invisible!
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)# important if you want text beside icon
        self.addToolBar(self.toolbar)
        self.tb_label=QLabel("toolbar")
        self.tb_label_mode=QLabel("Analysis Mode")

        self.tb_btn = QPushButton("log out")
        self.tb_btn.pressed.connect(self.go_to_login_page)
        self.mode_choice=QComboBox(self)
        self.mode_choice.addItem("Real Time")
        self.mode_choice.addItem("BackTesting")
        self.mode_choice.activated[str].connect(self.onModeSelected)

        self.toolbar.addWidget(self.tb_label)
        self.toolbar.addWidget(self.tb_btn)
        self.toolbar.addWidget(self.tb_label_mode)
        self.toolbar.addWidget(self.mode_choice)


        self.toolbar.setVisible(False)


        self.pages_layout = QStackedLayout() #here is where all pages are stored


        login_page=Login_page(self)
        self.main_page=Main_page(self)
        self.pages_layout.addWidget(login_page) #index 0  
        self.pages_layout.addWidget(self.main_page) #index 1

        self.pages_layout.setCurrentIndex(0) #set the initial page as the login one

        widget = QWidget()
        widget.setLayout(self.pages_layout)
        self.setCentralWidget(widget)

    #functions
    def go_to_main_page(self):
        print("go to main page")
        self.pages_layout.setCurrentIndex(1)
        self.toolbar.setVisible(True)
    def go_to_login_page(self):
        print("go to login page")
        self.pages_layout.setCurrentIndex(0)
        self.toolbar.setVisible(False)
    def onModeSelected(self,selected_mode):
        print("you selected",selected_mode)
        if selected_mode=="Real Time":
            self.main_page.mode_frame_layout.setCurrentIndex(1)
        elif selected_mode=="BackTesting":
            self.main_page.mode_frame_layout.setCurrentIndex(0)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()