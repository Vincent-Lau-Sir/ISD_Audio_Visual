from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import cv2
from enum import Enum

import numpy as np

display_monitor= 0
NUM_BUTTON_WIDTH = 100
NUM_BUTTON_HEIGHT = 100


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while True:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)

class APP_PAGE(Enum):
        MAIN = 0
        SETTING = 1
        
class Frequency_Selection(Enum):
        LPF_6K = 0
        LPF_12K = 1
        LPF_18K = 2
        LPF_FULL = 3

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISD Mic array Project")
        self.disply_width = 1280
        self.display_height = 720
        self.LPF_Select = Frequency_Selection.LPF_FULL.value
        self.ButtonText = QFont("Arial", 15)
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setFixedSize(1920,1080)
        # create a text label
        self.index = APP_PAGE.MAIN.value


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stacked_widget)

        self.ExitButton = QPushButton()
        self.ExitButton.clicked.connect(self.Exit)
        self.ExitButton.setFixedSize(NUM_BUTTON_WIDTH,NUM_BUTTON_HEIGHT)
        self.ExitButton.setText("Exit")
        self.ExitButton.setFont(self.ButtonText)
        

        self.SettingButton = QPushButton()
        self.SettingButton.clicked.connect(self.switchPage)
        self.SettingButton.setFixedSize(NUM_BUTTON_WIDTH,NUM_BUTTON_HEIGHT)
        self.SettingButton.setText("Setting")
        self.SettingButton.setFont(self.ButtonText)


        #Setting Up Main Page 
        self.MainPage = QGridLayout()
        self.MainPage.addWidget(self.image_label,0,0,1,3)


        self.RecordButton = QPushButton()
        # self.RecordButton.clicked.connect(self.Record_video)
        self.RecordButton.setFixedSize(NUM_BUTTON_WIDTH,NUM_BUTTON_HEIGHT)
        self.RecordButton.setText("Record")
        self.RecordButton.setFont(self.ButtonText)

        # self.MainPage.addWidget(self.textLabel,1,2,1,2)
        self.MainPage.addWidget(self.ExitButton,1,0,3,1)
        self.MainPage.addWidget(self.RecordButton,1,1,3,1)
        self.MainPage.addWidget(self.SettingButton,1,2,3,1)

        self.MainPageWidget = QWidget()
        self.MainPageWidget.setLayout(self.MainPage)

        #Setting up Setting page for LPF and Gain and Voulme 
        self.SettingPage = QGridLayout()

        self.GainLabel = QLabel("Mic Array Channel Gain")
        self.GainLabel.setFont(self.ButtonText)
        self.GainFader=QSlider(Qt.Horizontal)
        self.GainFader.setMinimum(-12)
        self.GainFader.setMaximum(12)
        self.GainFader.setValue(0)
        self.GainFader.setTickPosition(QSlider.TicksBelow)
        self.GainFader.setTickInterval(3)

        self.VolumeLabel = QLabel("Mic Array Digital Volume")
        self.VolumeLabel.setFont(self.ButtonText)

        self.VolumeFader=QSlider(Qt.Horizontal)
        self.VolumeFader.setMinimum(0)
        self.VolumeFader.setMaximum(24)
        self.VolumeFader.setValue(0)
        self.VolumeFader.setTickPosition(QSlider.TicksBelow)
        self.VolumeFader.setTickInterval(3)

        self.FilterSelectLabel = QLabel("Mic Array Filter Select")
        self.FilterSelectLabel.setFont(self.ButtonText)


        self.CheckBox_6kHz = QCheckBox('6kHz') 
        self.CheckBox_6kHz.setGeometry(200, 150, 100, 30) 
        self.CheckBox_6kHz.setChecked(False) 
        # self.CheckBox_6kHz.stateChanged.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_6K.value))        


        self.CheckBox_12kHz = QCheckBox('12kHz') 
        self.CheckBox_12kHz.setGeometry(200, 150, 100, 30) 
        self.CheckBox_12kHz.setChecked(False) 
        # self.CheckBox_12kHz.stateChanged.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_12K.value))   
        #


        self.CheckBox_18kHz = QCheckBox('18kHz') 
        self.CheckBox_18kHz.setGeometry(200, 150, 100, 30) 
        self.CheckBox_18kHz.setChecked(True) 
        # self.CheckBox_18kHz.stateChanged.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_18K.value))   
   

        self.CheckBox_Full = QCheckBox('Full Range') 
        self.CheckBox_Full.setGeometry(200, 150, 100, 30) 
        self.CheckBox_Full.setChecked(True) 
        # self.CheckBox_Full.stateChanged.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_FULL.value))   

        self.BackButton = QPushButton()
        self.BackButton.clicked.connect(self.switchPage)
        self.BackButton.setFixedSize(NUM_BUTTON_WIDTH,NUM_BUTTON_HEIGHT)
        self.BackButton.setText("Back")
        self.BackButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.BackButton.setFont(self.ButtonText)


        


        self.SettingPage.addWidget(self.GainLabel,1,0)
        self.SettingPage.addWidget(self.GainFader,1,1,1,4)
        # self.MainPage.addWidget(self.textLabel,1,2,1,2)
        self.SettingPage.addWidget(self.VolumeLabel,2,0)
        self.SettingPage.addWidget(self.VolumeFader,2,1,1,4)
        self.SettingPage.addWidget(self.FilterSelectLabel,3,0)

        self.SettingPage.addWidget(self.CheckBox_6kHz,3,1)
        self.SettingPage.addWidget(self.CheckBox_12kHz,3,2)
        self.SettingPage.addWidget(self.CheckBox_18kHz,3,3)
        self.SettingPage.addWidget(self.CheckBox_Full,3,4)

        self.SettingPage.addWidget(self.BackButton,4,0,1,2)
        
        
        self.SettingPageWidget = QWidget()
        self.SettingPageWidget.setLayout(self.SettingPage)
        self.SettingPageWidget.setFixedSize(700,400)
        self.SettingPageWidget.setGeometry(int((1920-700)/2),int((1080-400)/2),700,400)


        self.stacked_widget.addWidget(self.MainPageWidget)
        self.stacked_widget.addWidget(self.SettingPageWidget)

        self.ToggleSelection(Frequency_Selection.LPF_FULL.value)

        # self.stacked_widget.(self.MainPage)
        self.layout.addWidget(self.stacked_widget)

        # create a vertical box layout and add the two labels
        # vbox = QVBoxLayout()
        # vbox.addWidget(self.image_label)
        # vbox.addWidget(self.textLabel)
        # set the vbox layout as the widgets layout
        self.setLayout(self.layout)
        self.setFixedSize(1920,1080)
 

        # self.Monitor = QDesktopWidget().screenGeometry(display_monitor)
        self.setGeometry(QApplication.screens()[1].geometry())
        # self.setGeometry(self.Monitor.left(),self.Monitor.right())
        # self.showFullScreen()
        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()



    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    def ToggleSelection(self,choice):
        self.LPF_Select = choice
        list_of_range = [self.CheckBox_6kHz,self.CheckBox_12kHz,self.CheckBox_18kHz,self.CheckBox_Full]
        for i in range (len(list_of_range)):
                if i != choice:
                    list_of_range[i].setChecked(False)
                    list_of_range[i].setEnabled(True)
                else:
                     list_of_range[i].setChecked(True)
                     list_of_range[i].setEnabled(False)
                # else:
                    # list_of_range[i].setChecked(False)
                  

    def switchPage(self):
        self.index+=1 
        if (self.index > 1 ):
            
            self.index = 0
            
        next_index = self.index % self.stacked_widget.count()  # Cycle through the pages
        self.stacked_widget.setCurrentIndex(next_index)

    def Exit(self):
        exit()
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())