import sys
import random
import time
import numpy as np
import datetime
import matplotlib
import pandas as pd
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt,QDate,QDateTime
from PyQt5.QtWidgets import QApplication, QComboBox, QLabel, QMainWindow, QSizePolicy, QVBoxLayout, QWidget,QHBoxLayout,QGridLayout,QStackedLayout,QPushButton,QToolBar,QSpacerItem,QLineEdit,QDateTimeEdit,QFormLayout,QDoubleSpinBox,QMessageBox
from PyQt5.QtGui import QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from scripts.functions import *
from operator import itemgetter 


GENERAL_PATH=os.getcwd()
config_dict=read_yaml(GENERAL_PATH+"/config.yaml")
DATETIME_FORMAT=config_dict["CONFIG"]["datetime"]


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
        self.fig, self.axes = plt.subplots(figsize=(5, 4), dpi=200)
        self.max_x_ticks=10 # you can personalise it in order to select the thickness of the plot
        
        super(MplCanvas, self).__init__(self.fig)



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
        super().__init__(parent)
        self.Parent=self.parent()
        #layout definition
        self.main_layout=QHBoxLayout()
        self.column1_layout = QStackedLayout()# in base a quale modalità scelgo, cambiano i parametri da visualizzare
        self.column1_layout.setCurrentIndex(0) # imposto la modalità Realtime come quella iniziale
        self.column2_layout = QStackedLayout()
        self.column2_layout.setCurrentIndex(0)
        self.column3_layout=QVBoxLayout()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
# ---------------------------------------------------------------------------- #
#                              Backtesting Layout                              #
# ---------------------------------------------------------------------------- #


# --------------------------------- column 1 --------------------------------- #
        self.backtesting_column1_layout=QVBoxLayout()
        self.backtesting_column1_widget=QWidget() #creo widget in cui metto il layout di backtesting
        self.backtesting_column1_widget.setLayout(self.backtesting_column1_layout)
        
        self.column1_layout.addWidget(self.backtesting_column1_widget) # aggiungo nel layout delle modalità i widget rappresentanti le n modalità


        self.backtesting_label=QLabel("Parametri BackTesting")

        parameters_form_layout = QFormLayout(self.backtesting_column1_widget) # form layout in which i put a label with all the parameters to be setted
        self.init_date=QDateTimeEdit(QDateTime(2021,9,1,00,00,00),self.backtesting_column1_widget)
        self.end_date=QDateTimeEdit(QDateTime.currentDateTime(),self.backtesting_column1_widget) #these two widget define the period that needs to be analysed
        
        investing_amount_bt=QDoubleSpinBox(self.backtesting_column1_widget)
        investing_amount_bt.setMinimum(1)
        investing_amount_bt.setMaximum(1000)
        investing_amount_bt.setPrefix("$") #TODO: when you change currencies, change prefix
        #region currencies choice
        self.crypto_currencies_choice_bt=QComboBox(self.backtesting_column1_widget)
        self.crypto_currencies_choice_bt.addItem("BTC-USD")
        self.crypto_currencies_choice_bt.addItem("BTC-EUR")
        self.crypto_currencies_choice_bt.addItem("ETH-EUR")
        self.crypto_currencies_choice_bt.addItem("ETH-USD")
        #endregion
        #region marketplace choice
        self.marketplace_crypto_choice_bt=QComboBox(self.backtesting_column1_widget)
        self.marketplace_crypto_choice_bt.addItem("coinbase")
        self.marketplace_crypto_choice_bt.addItem("binance")
        self.marketplace_crypto_choice_bt.addItem("market3")
        #endregion

        parameters_form_layout.addRow(self.tr("from:"), self.init_date)
        parameters_form_layout.addRow(self.tr("to:"), self.end_date)
        parameters_form_layout.addRow(self.tr("investing amount"),investing_amount_bt)
        parameters_form_widget=QWidget()
        parameters_form_widget.setLayout(parameters_form_layout)

        self.analise_button=QPushButton("analise")
        self.analise_button.clicked.connect(self.analise)
        

        self.backtesting_column1_layout.addWidget(self.backtesting_label)
        self.backtesting_column1_layout.addWidget(self.crypto_currencies_choice_bt)
        self.backtesting_column1_layout.addWidget(self.marketplace_crypto_choice_bt)
        self.backtesting_column1_layout.addWidget(parameters_form_widget)
        self.backtesting_column1_layout.addWidget(self.analise_button)
        self.backtesting_column1_layout.addStretch(1) #push the object up in the frame


# --------------------------------- column 2 --------------------------------- #

        self.backtesting_column2_layout=QVBoxLayout()
        self.backtesting_column2_layout_widget=QWidget()
        self.backtesting_column2_layout_widget.setLayout(self.backtesting_column2_layout)
        self.column2_layout.addWidget(self.backtesting_column2_layout_widget)

        self.second_column_label=QLabel("Grafico Backtesting")
        self.backtesting_column2_layout.addWidget(self.second_column_label)
        
        self.canvas = MplCanvas(self, width=8, height=4, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.test_x_data=[0.2,2,3,4,5,6,7,8,9]
        self.test_y_data=[0.3,3,5,3,7,5,2,2,6]
        self.old_test_y=self.test_y_data
        self.canvas.axes.plot(self.test_x_data, self.test_y_data,'r',label="line 1")
        self.canvas.draw()
        
        self.backtesting_column2_layout.addWidget(self.canvas)
        self.backtesting_column2_layout.addWidget(self.toolbar)
       
        self.backtesting_column2_layout.addStretch(1)

        

# ---------------------------------------------------------------------------- #
#                                Real Time Frame                               #
# ---------------------------------------------------------------------------- #


# --------------------------------- column 1 --------------------------------- #
        self.realtime_column1_layout=QVBoxLayout()
        self.realtime_column1_widget=QWidget()    ##creo widget in cui metto il layout di Realtime
        self.realtime_column1_widget.setLayout(self.realtime_column1_layout)
        self.column1_layout.addWidget(self.realtime_column1_widget)    # aggiungo nel layout delle modalità i widget rappresentanti le n modalità
        
        
        self.realtime_label=QLabel("Parametri RealTime")
        self.crypto_currencies_choice_rt=QComboBox(self.realtime_column1_widget)
        self.crypto_currencies_choice_rt.addItem("BTC-USD")
        self.crypto_currencies_choice_rt.addItem("BTC-EUR")
        self.crypto_currencies_choice_rt.addItem("ETH-EUR")
        self.crypto_currencies_choice_rt.addItem("ETH-USD")
        self.marketplace_crypto_choice_rt=QComboBox(self.realtime_column1_widget)
        self.marketplace_crypto_choice_rt.addItem("market1")
        self.marketplace_crypto_choice_rt.addItem("market2")
        self.marketplace_crypto_choice_rt.addItem("market3")
        investing_amount_rt=QDoubleSpinBox(self.realtime_column1_widget)
        investing_amount_rt.setMinimum(1)
        investing_amount_rt.setMaximum(1000)
        investing_amount_rt.setPrefix("$") #TODO: when you change currencies, change prefix
        self.realtime_column1_layout.addWidget(self.realtime_label)
        self.realtime_column1_layout.addWidget(self.crypto_currencies_choice_rt)
        self.realtime_column1_layout.addWidget(self.marketplace_crypto_choice_rt)
        self.realtime_column1_layout.addWidget(investing_amount_rt)
        self.realtime_column1_layout.addStretch(1) #push the object up in the frame

# --------------------------------- column 2 --------------------------------- #

        self.realtime_column2_layout=QVBoxLayout()
        self.realtime_column2_layout_widget=QWidget()
        self.realtime_column2_layout_widget.setLayout(self.realtime_column2_layout)
        self.column2_layout.addWidget(self.realtime_column2_layout_widget)

        self.second_column_label=QLabel("Grafico RealTime")
        self.realtime_column2_layout.addWidget(self.second_column_label)
        
        self.canvas2 = MplCanvas(self, width=8, height=4, dpi=100)
        self.toolbar2 = NavigationToolbar(self.canvas2, self)
        self.realtime_column2_layout.addWidget(self.canvas2)
        self.realtime_column2_layout.addWidget(self.toolbar2)

        
        #this creates some initials random data
        self.counter=0
        self.n_data = 10
        self.x1data = list(range(self.counter,self.n_data+self.counter))
        self.y1data = [random.randint(0, 10) for i in range(self.n_data)]
        self.x2data = list(range(self.counter,self.n_data+self.counter))
        self.y2data = [random.randint(0, 10) for i in range(self.n_data)]


        self.update_plot()
        self.show()
        
        self.realtime_column2_layout.addStretch(1)


 # ---------------------------------------------------------------------------- #
 #                 column 3 - for both backtesting and realtime                 #
 # ---------------------------------------------------------------------------- #

        result_column3_label=QLabel("Results:")
        self.init_date_label=QLabel()
        self.end_date_label=QLabel()
        self.balance_label=QLabel()
        #set the text alignment
        result_column3_label.setAlignment(Qt.AlignCenter)
        self.init_date_label.setAlignment(Qt.AlignRight)
        self.end_date_label.setAlignment(Qt.AlignRight)
        self.balance_label.setAlignment(Qt.AlignRight)

        self.init_date_layout=QFormLayout()
        self.init_date_layout.addRow(self.tr("From:"),self.init_date_label)
        self.end_date_layout=QFormLayout()
        self.end_date_layout.addRow(self.tr("To:"),self.end_date_label)
        self.balance_layout=QFormLayout()
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

        #adding widgets to the column layout
        self.column3_layout.addWidget(result_column3_label)
        self.column3_layout.addWidget(self.init_date_label_widget)
        self.column3_layout.addWidget(self.end_date_label_widget)
        self.column3_layout.addWidget(self.balance_label_widget)
        self.column3_layout.addStretch(1) #push the object up in the frame

        
# ---------------------------------------------------------------------------- #
#                      Adding sub-windows to the main page                     #
# ---------------------------------------------------------------------------- #
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
 # --------------------------- get some random data --------------------------- #
        self.x1data = list(range(self.counter,self.n_data+self.counter))
        self.y1data = self.y1data[1:] + [random.randint(0, 20)]
        self.x2data = list(range(self.counter,self.n_data+self.counter))
        self.y2data = self.y2data[1:] + [random.randint(0, 20)]

 # --------------------------- about realtime graph --------------------------- #
        if self.Parent.activated_realtime_graph == True:
            self.canvas2.axes.cla()  # Clear the canvas.
            self.canvas2.axes.plot(self.x1data, self.y1data, 'r',label="line 1")
            self.canvas2.axes.plot(self.x2data, self.y2data, 'b', label="line 2")
            self.canvas2.axes.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=3)
            self.canvas2.draw()  
            self.counter+=1

# -------------------------- about backtesting graph ------------------------- #
        #if data shown changes, then we updaye the passed in the figure (graph)
        
        if self.test_y_data!=self.old_test_y:
            self.canvas.axes.cla()
            #self.canvas.axes.plot(self.test_x_data,self.test_y_data,'b',label="line 1")
            #print(self.data["unix_time"])
            datetime_unix_list=list(self.data["unix_time"])
            datetime_strinf_list=list(self.data["string_time"])
            high=list(self.data["high"])
            filtered_datetime,filtered_high=self.adjust_periods_for_plotting(datetime_unix_list,high)
            self.canvas.axes.plot(filtered_datetime,filtered_high,'b',label="line 1")
            x_tick=[] # here ticks will be stored 
            f = lambda m, n: [i*n//m + n//(2*m) for i in range(m)] # function that even select elements ,'m' is how many element u wnat to pick, 'n' the length of the rrray
            idx=f(self.canvas.max_x_ticks,len(filtered_datetime))     
            x_tick=(itemgetter(*idx)(filtered_datetime)) #here it return the sublist with the evenly spaced elements
            self.canvas.axes.set_xticks(x_tick) # set plotted tick
            self.canvas.axes.set_xticklabels(x_tick,rotation=45, ha="right") # set labels configuration
            
            #self.canvas.axes.set_yticklabels()
            self.canvas.draw()
       # print(self.xdata)
        self.old_test_y=self.test_y_data
    def adjust_periods_for_plotting(self,*args):
        """This function reduces the sticks used during plotting. The reductionm is based on the length of the 
           period analysed.

        Args:
            x (list): x axis to be adapted in order to reduce plotting time
            y (list): y axis to be adapted in order to reduce plotting time

        Returns:
            new_x (list): adapted x axis
            new_y (list): adapted y axis
        """
        x=args[0]
        y=args[1]
        #converting the first and last element to datetime obj
        start_datetime=datetime.fromtimestamp(int(x[0]))
        end_datetime=datetime.fromtimestamp(int(x[-1]))
        #checking the length of the period
        period=end_datetime-start_datetime
        unit_period=period/20 # this is the difference of time between each stick plotted
        unit_period_in_minutes=round(unit_period.seconds% 3600 / 60.0)## i get an integer representing the minutes between each plotted stuc
        #print(start_datetime,end_datetime,period,unit_period_in_minutes)
        #now you can loop through the x axis and filter only the ones with the datetime selected.
        filtered_x=x[::unit_period_in_minutes]
        filtered_y=y[::unit_period_in_minutes]
       # print("filtered_x",filtered_x)
       # print("x",x)

        return filtered_x,filtered_y
    def analise(self): # 
        #in this function, i get all the parameters and start to analise them
        
            #here i convert the dates the user has selected
        init_date_string=self.init_date.dateTime().toPyDateTime()
        end_date_string=self.end_date.dateTime().toPyDateTime() # dateTime() returns QDateTime, toPyDateTime() converts to datetime.datetime
        marketplace_string=str(self.marketplace_crypto_choice_bt.currentText())
        coin_chosen_string=str(self.crypto_currencies_choice_bt.currentText())
        self.data=get_data_graph(init_date_string,end_date_string,marketplace_string,coin_chosen_string)
        state=checkDate(init_date_string.timestamp(),end_date_string.timestamp())# timestamp converts into unix format, useful in order to make some checks
        test_x_data=[1,2,3,4,5,6,7,8,9]
        test_y_data=[random.randint(0, 10) for i in range(9)]
        self.test_y_data=test_y_data

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


 
