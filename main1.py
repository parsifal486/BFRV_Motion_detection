import sys
import platform
from Ui_main1 import Ui_MainWindow
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import (QThread, QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
import PySide6.QtWidgets as qw
import Ui_main1

import serial
import time 
import threading
import re


# GLOBALS
counter = 0
datas = []

class SerialFrom():
    def __init__(self):
        super().__init__()
        self.ui = Ui_main1.Ui_MainWindow()
        self.ui.setupUi(self)
        
        


## ==> YOUR APPLICATION WINDOW
class SerialWindow(qw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## ==> SET VALUES TO DEF progressBarValue
        def setValue(self, slider, labelPercentage, progressBarName, color):

            # GET SLIDER VALUE
            value = slider.value()

            # CONVERT VALUE TO INT
            sliderValue = int(value)

            # HTML TEXT PERCENTAGE
            htmlText = """<p align="center"><span style=" font-size:50pt;">{VALUE}</span><span style=" font-size:40pt; vertical-align:super;">%</span></p>"""
            labelPercentage.setText(htmlText.replace("{VALUE}", str(sliderValue)))

            # CALL DEF progressBarValue
            self.progressBarValue(sliderValue, progressBarName, color)

        # open serial port and set parameters
        self.ser = serial.Serial('COM4', 9600, timeout=1)

        # initiate the thread
        self.is_reading = True
        self.read_thread = threading.Thread(target=self.readSerialData)
        self.read_thread.start()

        ## ==> DEF START VALUES
        self.ui.sliderA.setValue(0)


        ## ==> APPLY VALUES TO PROGREESBAR
        self.ui.sliderA.valueChanged.connect(lambda: setValue(self, self.ui.sliderA, self.ui.labelPercentageA, self.ui.circularProgressA, "rgba(85, 170, 255, 255)"))

    ## DEF PROGRESS BAR VALUE
    ########################################################################
    def progressBarValue(self, value, widget, color):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 110px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # FIX MAX VALUE
        if value == 100:
            stop_1 = "1.000"
            stop_2 = "1.000"

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2).replace("{COLOR}", color)

        # APPLY STYLESHEET WITH NEW VALUES
        widget.setStyleSheet(newStylesheet)

    def readSerialData(self):
        while self.is_reading:
            data = self.ser.readline()
            global counter,datas
            if data:
                print(type(data))
                print(data[1])
                if(counter<20):
                    datas.append(data[1])
                    counter = counter + 1
                else:
                    self.stateUpdate(datas)
                    counter = 0
                    datas= []
            time.sleep(0.1)
    
    def closeEvent(self, event):
        # close the thread
        self.is_reading = False
        self.read_thread.join()
        self.ser.close()
        event.accept()

    def stateUpdate(self, nums):
        mean = average = sum(nums) / len(nums)
        deviation = sum([(x - mean)**2 for x in nums]) / len(nums)
        print('deviation',deviation)
        if deviation > 20:
            self.ui.label_stat.setText("激烈运动")
        if deviation <= 20 and deviation >16:
            self.ui.label_stat.setText("中等运动")
        if deviation < 16:
            self.ui.label_stat.setText("几乎静止")
        self.ui.sliderA.setValue(deviation*4)

if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    window = SerialWindow()
    window.show()
    sys.exit(app.exec())
