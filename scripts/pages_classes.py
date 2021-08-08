import sys
import random
import time
import datetime
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QComboBox, QLabel, QMainWindow, QSizePolicy, QVBoxLayout, QWidget,QHBoxLayout,QGridLayout,QStackedLayout,QPushButton,QToolBar,QSpacerItem,QLineEdit,QDateTimeEdit,QFormLayout,QDoubleSpinBox,QMessageBox
from PyQt5.QtGui import QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from scripts.functions import *


class proto_page(QWidget): #prototype of page widget to be used in a QStackedLayout

    def __init__(self,parent=None):
        super().__init__()
        self.proto_layout=QVBoxLayout()
        self.setLayout(self.proto_layout)
        self.proto_btn = QPushButton("proto")
        self.proto_btn.pressed.connect(parent.go_to_main_page)
        self.proto_layout.addWidget(self.proto_btn)

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.axes = plt.subplots(figsize=(5, 4), dpi=200)
        super(MplCanvas, self).__init__(fig)



class Login_page(QWidget):

    def __init__(self,parent=None):
        super().__init__()
        
        login_layout=QHBoxLayout()

        form_layout=QVBoxLayout()
        form_layout.setSpacing(10)
        log_btn = QPushButton("log in")
        log_btn.pressed.connect(parent.go_to_main_page)
        username = QLineEdit()
        username.setMaxLength(50)
        username.setPlaceholderText("Enter your username")
        password = QLineEdit()
        password.setMaxLength(500)
        password.setPlaceholderText("Enter your password")
        verticalSpacerUp = QSpacerItem(0, 300, QSizePolicy.Expanding, QSizePolicy.Minimum) 
        verticalSpacerDown = QSpacerItem(0, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)
        form_layout.addItem(verticalSpacerUp)
        form_layout.addWidget(username)
        form_layout.addWidget(password)
        form_layout.addWidget(log_btn)
        form_layout.addItem(verticalSpacerDown)
        form_box=QWidget()
        form_box.setLayout(form_layout)
        
        #this spacer are used to center the login form in the login page
        horizontalSpacerSx = QSpacerItem(500, 0, QSizePolicy.Minimum, QSizePolicy.Expanding) 
        horizontalSpacerDx = QSpacerItem(500, 0, QSizePolicy.Minimum, QSizePolicy.Expanding) 

        login_layout.addItem(horizontalSpacerSx)
        login_layout.addWidget(form_box)
        login_layout.addItem(horizontalSpacerDx)

        self.setLayout(login_layout)
        
       

class Main_page(QWidget): #prototype of page widget to be used in a QStackedLayout

    def __init__(self,parent=None):
        super().__init__()

        #layout definition
        self.main_layout=QHBoxLayout()
        self.column1_layout=QVBoxLayout()
        self.column2_layout=QVBoxLayout()
        self.column3_layout=QVBoxLayout()

        ####first column####
        self.mode_frame_layout = QStackedLayout()# in base a quale modalità scelgo, cambiano i parametri da visualizzare
        self.mode_backtesting_layout=QVBoxLayout()
        self.mode_realtime_layout=QVBoxLayout()
        self.mode_backtesting_frame=QWidget() #creo widget in cui metto il layout di backtesting
        self.mode_realtime_frame=QWidget()    ##creo widget in cui metto il layout di Realtime
        self.mode_backtesting_frame.setLayout(self.mode_backtesting_layout)
        self.mode_realtime_frame.setLayout(self.mode_realtime_layout)
        self.mode_frame_layout.addWidget(self.mode_backtesting_frame) # aggiungo nel layout delle modalità i widget rappresentanti le n modalità
        self.mode_frame_layout.addWidget(self.mode_realtime_frame)    # aggiungo nel layout delle modalità i widget rappresentanti le n modalità
        self.mode_frame_layout.setCurrentIndex(1) # imposto la modalità Realtime come quella iniziale
        self.mode_frame_widget=QWidget()
        self.mode_frame_widget.setLayout(self.mode_frame_layout)
        self.column1_layout.addWidget(self.mode_frame_widget)
        self.column1_layout.addStretch(1)


            #backtesting frame

        self.backtesting_label=QLabel("Parametri BackTesting")

        parameters_form_layout = QFormLayout(self.mode_backtesting_frame) # form layout in which i put a label with all the parameters to be setted
        self.init_date=QDateTimeEdit(self.mode_backtesting_frame)
        self.end_date=QDateTimeEdit(self.mode_backtesting_frame) #these two widget define the period that needs to be analysed
        investing_amount=QDoubleSpinBox(self.mode_backtesting_frame)
        investing_amount.setMinimum(1)
        investing_amount.setMaximum(1000)
        investing_amount.setPrefix("$") #TODO: when you change currencies, change prefix
        crypto_currencies_choice=QComboBox(self.mode_backtesting_frame)
        crypto_currencies_choice.addItem("BTC-EUR")
        crypto_currencies_choice.addItem("BTC-USD")
        crypto_currencies_choice.addItem("ETH-EUR")
        crypto_currencies_choice.addItem("ETH-USD")
        marketplace_crypto_choice=QComboBox(self.mode_backtesting_frame)
        marketplace_crypto_choice.addItem("market1")
        marketplace_crypto_choice.addItem("market2")
        marketplace_crypto_choice.addItem("market3")

        parameters_form_layout.addRow(self.tr("from:"), self.init_date)
        parameters_form_layout.addRow(self.tr("to:"), self.end_date)
        parameters_form_layout.addRow(self.tr("investing amount"),investing_amount)
        parameters_form_widget=QWidget()
        parameters_form_widget.setLayout(parameters_form_layout)

        analise_button=QPushButton("analise")
        analise_button.pressed.connect(self.analise)
        self.mode_backtesting_layout.addWidget(self.backtesting_label)
        self.mode_backtesting_layout.addWidget(crypto_currencies_choice)
        self.mode_backtesting_layout.addWidget(marketplace_crypto_choice)
        self.mode_backtesting_layout.addWidget(parameters_form_widget)#
        self.mode_backtesting_layout.addWidget(analise_button)

        self.mode_backtesting_layout.addStretch(1) #push the object up in the frame
    
        

            #Real Time Frame

        self.realtime_label=QLabel("Parametri RealTime")
        crypto_currencies_choice=QComboBox(self.mode_realtime_frame)
        crypto_currencies_choice.addItem("BTC-EUR")
        crypto_currencies_choice.addItem("BTC-USD")
        crypto_currencies_choice.addItem("ETH-EUR")
        crypto_currencies_choice.addItem("ETH-USD")
        marketplace_crypto_choice=QComboBox(self.mode_realtime_frame)
        marketplace_crypto_choice.addItem("market1")
        marketplace_crypto_choice.addItem("market2")
        marketplace_crypto_choice.addItem("market3")
        investing_amount=QDoubleSpinBox(self.mode_realtime_frame)
        investing_amount.setMinimum(1)
        investing_amount.setMaximum(1000)
        investing_amount.setPrefix("$") #TODO: when you change currencies, change prefix
        self.mode_realtime_layout.addWidget(self.realtime_label)
        self.mode_realtime_layout.addWidget(crypto_currencies_choice)
        self.mode_realtime_layout.addWidget(marketplace_crypto_choice)
        self.mode_realtime_layout.addWidget(investing_amount)
        self.mode_realtime_layout.addStretch(1) #push the object up in the frame

        

        #####second column####  the graph about real time 
        self.second_column_label=QLabel("Grafico")
        self.column2_layout.addWidget(self.second_column_label)
        
        self.canvas = MplCanvas(self, width=8, height=4, dpi=100)
        self.column2_layout.addWidget(self.canvas)

        self.counter=0
        self.n_data = 10
        self.x1data = list(range(self.counter,self.n_data+self.counter))
        self.y1data = [random.randint(0, 10) for i in range(self.n_data)]

        self.x2data = list(range(self.counter,self.n_data+self.counter))
        self.y2data = [random.randint(0, 10) for i in range(self.n_data)]
        self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        self.column2_layout.addStretch(1) #push the object up in the frame

        ####third column####
        result_column3_label=QLabel("Results:")
        self.init_date_label=QLabel()
        self.end_date_label=QLabel()
        self.balance_label=QLabel()
        #set the text alignment
        self.init_date_label.setAlignment(Qt.AlignRight)
        self.end_date_label.setAlignment(Qt.AlignRight)
        self.balance_label.setAlignment(Qt.AlignRight)

        self.init_date_layout=QFormLayout()
        self.end_date_layout=QFormLayout()
        self.balance_layout=QFormLayout()
        self.init_date_layout.addRow(self.tr("From:"),self.init_date_label)
        self.end_date_layout.addRow(self.tr("To:"),self.end_date_label)
        self.balance_layout.addRow(self.tr("Balance:"),self.balance_label)

        #creation of the widget used for the several layouts inside the column
        self.init_date_label_widget=QWidget()
        self.end_date_label_widget=QWidget()
        self.balance_label_widget=QWidget()
        #setting the layouts to the proper widget
        self.init_date_label_widget.setLayout(self.init_date_layout)
        self.end_date_label_widget.setLayout(self.end_date_layout)
        self.balance_label_widget.setLayout(self.balance_layout)
        #visible only when 'analise' button is pressed
        self.init_date_label_widget.setVisible(False) 
        self.end_date_label_widget.setVisible(False) 
        self.balance_label_widget.setVisible(False)  

        result_column3_label.setAlignment(Qt.AlignCenter)
        #adding widgets to the column layout
        self.column3_layout.addWidget(result_column3_label)
        self.column3_layout.addWidget(self.init_date_label_widget)
        self.column3_layout.addWidget(self.end_date_label_widget)
        self.column3_layout.addWidget(self.balance_label_widget)
        self.column3_layout.addStretch(1) #push the object up in the frame

        
        ####adding the three columns to the main page####
        
        column1_frame=QWidget()
        column1_frame.setLayout(self.column1_layout)
        column2_frame=QWidget()
        column2_frame.setLayout(self.column2_layout)
        column3_frame=QWidget()
        column3_frame.setLayout(self.column3_layout)
        column1_frame.setFixedWidth(300)
        column2_frame.setMinimumWidth(600)
        column3_frame.setFixedWidth(280)
        self.main_layout.addWidget(column1_frame)
        self.main_layout.addWidget(column2_frame)
        self.main_layout.addWidget(column3_frame)

        self.setLayout(self.main_layout)
    def update_plot(self):
        # Drop off the first y element, append a new one.
        self.x1data = list(range(self.counter,self.n_data+self.counter))
        self.y1data = self.y1data[1:] + [random.randint(0, 20)]
        self.x2data = list(range(self.counter,self.n_data+self.counter))
        self.y2data = self.y2data[1:] + [random.randint(0, 20)]

        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.x1data, self.y1data, 'r',label="line 1")
        self.canvas.axes.plot(self.x2data, self.y2data, 'b', label="line 2")
        self.canvas.axes.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=3)
    
        # Trigger the canvas to update and redraw.
        self.canvas.draw()
        
        self.counter+=1
       # print(self.xdata)
    def analise(self): # 
        #in this function, i get all the parameters and start to analise them
        
            #here i convert the dates the user has selected
        init_date_string=self.init_date.dateTime().toPyDateTime()
        end_date_string=self.end_date.dateTime().toPyDateTime() # dateTime() returns QDateTime, toPyDateTime() converts to datetime.datetime
        state=checkDate(init_date_string.timestamp(),end_date_string.timestamp())# timestamp converts into unix format, useful in order to make some checks
        if state==True:
            self.init_date_label.setText(init_date_string.strftime('%Y-%m-%d %H:%M:%S'))
            self.end_date_label.setText(end_date_string.strftime('%Y-%m-%d %H:%M:%S'))
            self.balance_label.setText(self.getBalance())
            self.init_date_label_widget.setVisible(True)
            self.end_date_label_widget.setVisible(True)
            self.balance_label_widget.setVisible(True)
        else:
            self.showError(state) #creates a warning box with the desired message!
    def getBalance(self): #TODO: develop a function used to get a realistic result
        return "0"
    def showError(self,text):
        dlg = QMessageBox()  #built in dialog widget for specific type of messages
        dlg.setWindowTitle("Date range not valid!")
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Critical)
        button = dlg.exec()