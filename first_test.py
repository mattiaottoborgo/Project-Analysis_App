import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.button_is_checked = True #variable in which i save the state of the button
        self.button = QPushButton("Press Me!")

        self.setFixedSize(QSize(400, 300)) #fix dimension to a specific size
        self.button.setFixedSize(QSize(100, 100))

        # Set the central widget of the Window.
        self.setCentralWidget(self.button)
        self.button.setCheckable(True)
        self.button.clicked.connect(self.the_button_was_clicked)
        self.button.clicked.connect(self.the_button_was_toggled) #check if button is on or off (remove this if u want just to click it)
        #self.button.released.connect(self.the_button_was_released) # useful for any widget
        # Set the central widget of the Window.
        self.setCentralWidget(self.button)




        self.label = QLabel()

        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText) #connect together two widgets directly

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

    def the_button_was_clicked(self):
        print("Clicked!")
        self.button.setText("You already clicked me.")
        self.button.setEnabled(False)
    def the_button_was_toggled(self, checked):
         self.button_is_checked = checked
         print(self.button_is_checked)
    def the_button_was_released(self): #retrieve the status of widget that doesn't do it automatically
        self.button_is_checked = self.button.isChecked()

        print(self.button_is_checked)



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()