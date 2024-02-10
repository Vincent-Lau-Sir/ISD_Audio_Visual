from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import cv2
from enum import Enum
from Style import *
import numpy as np
import sounddevice as sd 
import os 
import wavio #pip3 install wavio
display_monitor= 0
NUM_BUTTON_WIDTH = 200
NUM_BUTTON_HEIGHT = 100
DEBUG = True
BUTTON_FONT = QFont("Arial",40)
CURRENT_PATH = os.getcwd()

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(2)
        
        cap.set(3, 1920)
        cap.set(4, 1080)
        video_width = int(cap.get(3))
        video_height = int(cap.get(4))

        print(video_height,video_width)
        while True:
            ret, self.cv_img = cap.read()
            
            if ret:
                self.change_pixmap_signal.emit(self.cv_img)

class APP_PAGE(Enum):
        MAIN = 0
        SETTING = 1
        

class AudioThread(QThread):
    global STOP
    def run(self):
        sample_rate = 44100  # Hz
        duration = 10  # seconds
        self.audio_buffer = []  # Buffer to store recorded audio data

        # Use a callback function for non-blocking audio recording
        def callback(indata, frames, time, status):
            if status:
                print(status)
            # print("Recording audio...")
            self.audio_buffer.append(indata.copy())

        with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
            self.sleep(duration)
        
        # Convert the buffer to a numpy array
        audio_data = np.concatenate(self.audio_buffer, axis=0)

        # Save the audio data to a WAV file
        wavio.write("recorded_audio.wav", audio_data, sample_rate, sampwidth=3)
        print("Finsihed Recording")
        STOP=True




class Frequency_Selection(Enum):
        LPF_6K = 0
        LPF_12K = 1
        LPF_18K = 2
        LPF_FULL = 3

        def Frequency_list(self):
            return [self.LPF_6K,self.LPF_12K,self.LPF_18K,self.LPF_FULL] 

class App(QWidget):
    def __init__(self):
        super().__init__()
        if (QDesktopWidget().screenCount() >1):
            self.ScreenNumber = 1
        else:
            self.ScreenNumber = 0
        self.setWindowTitle("ISD Mic array Project")

        self.disply_width = 1920
        self.display_height = 1080
        self.LPF_Select = Frequency_Selection.LPF_FULL.value
        self.ButtonText = QFont("Arial", 15)
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.setText("Loading Camera Frame ...")
        self.image_label.setStyleSheet("")
        self.image_label.setFont(QFont("Arial",40))

        self.image_label.setFixedSize(1920,1080)

        self.image_label.setStyleSheet("background-color:Grey;border-width: 4px;border-radius: 20px;alignment:center")
        self.image_label.setContentsMargins(0,0,0,0)

        self.RECORDING = False
        

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setContentsMargins(0, 0, 0, 0)  # Set margins to zero
        
        self.stacked_widget.setFixedSize(1920,1080)
        # self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 green, stop:1 white);")
        self.setStyleSheet("background-color:lightgreen")
        
        # create a text label
        self.index = APP_PAGE.MAIN.value


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stacked_widget)
        self.layout.setContentsMargins(0,0,0,0)
      

     

        self.ExitButton = QPushButton()
        self.ExitButton.clicked.connect(self.Exit)
        self.ExitButton.setFixedSize(NUM_BUTTON_WIDTH,NUM_BUTTON_HEIGHT)
        self.ExitButton.setText("Exit")
        self.ExitButton.setFont(BUTTON_FONT )
        self.ExitButton.setStyleSheet(BUTTON_STYLE)

        self.SettingButton = QPushButton()
        self.SettingButton.clicked.connect(self.switchPage)
        self.SettingButton.setFixedSize(NUM_BUTTON_WIDTH,NUM_BUTTON_HEIGHT)
        self.SettingButton.setText("Setting")
        self.SettingButton.setFont(BUTTON_FONT)
        self.SettingButton.setStyleSheet(BUTTON_STYLE)


        self.text_label =QPlainTextEdit()
        self.text_label.setFixedSize(250,800)
        self.text_label.setStyleSheet("background-color: white ;")

        #Setting Up Main Page 
        self.MainPage = QGridLayout()
        self.MainPage.setHorizontalSpacing(0)  # Set horizontal spacing to zero   
        self.MainPage.setVerticalSpacing(0)
        # self.MainPage = QVBoxLayout()
        self.MainPage.addWidget(self.image_label,0,0,alignment=Qt.AlignCenter)
       
        
        if DEBUG == True:
            self.MainPage.addWidget(self.text_label,0,0,alignment=Qt.AlignRight)
        self.MainPage.setHorizontalSpacing(0)  # Set horizontal spacing to zero   
        self.MainPage.setVerticalSpacing(0)  # Set horizontal spacing to zero   
        # self.MainPage.addWidget(self.image_label)
        

        self.RecordButton = QPushButton()
        self.RecordButton.clicked.connect(self.Record_clicked)
        self.RecordButton.setFixedSize(NUM_BUTTON_WIDTH,NUM_BUTTON_HEIGHT)
        self.RecordButton.setText("Record")
        self.RecordButton.setFont(BUTTON_FONT )
        self.RecordButton.setStyleSheet(BUTTON_STYLE_RED)

        # self.MainPage.addWidget(self.textLabel,1,2,1,2)

        self.MainPage_button = QHBoxLayout()
        self.MainPage_button.addWidget(self.ExitButton,alignment=Qt.AlignLeft)
        self.MainPage_button.addWidget(self.RecordButton)
        self.MainPage_button.addWidget(self.SettingButton,alignment=Qt.AlignRight)

        self.MainPage_button_widget = QWidget()
        self.MainPage_button_widget.setLayout(self.MainPage_button)
        self.MainPage_button_widget.setStyleSheet("background-color:transparent")
        self.MainPage_button_widget.setFixedSize(1920,200)
        
        if DEBUG == True:
            self.MainPage.addWidget(self.MainPage_button_widget,1,0,1,2)
        else:
            self.MainPage.addWidget(self.MainPage_button_widget,0,0,alignment=Qt.AlignBottom)
             

        self.MainPageWidget = QWidget()
        self.MainPageWidget.setLayout(self.MainPage)
        self.MainPageWidget.setFixedSize(1920,1080)

        #Setting up Setting page for LPF and Gain and Voulme 
        self.SettingPage = QGridLayout()
        

        self.GainLabel = QLabel("Mic Array Channel Gain  :")
        self.GainLabel.setFont(BUTTON_FONT)
        self.GainFader=QSlider(Qt.Horizontal)
        self.GainFader.setMinimum(-12)
        self.GainFader.setMaximum(12)
        self.GainFader.setValue(0)
        self.GainFader.setTickPosition(QSlider.TicksBelow)
        self.GainFader.valueChanged.connect(self.update_label)
        self.GainFader.setTickInterval(1)
        self.GainFader.setFont(QFont("Arial",40))
        self.GainFader.setStyleSheet(SLIDER_STYLE)
        self.GainFader.setFixedWidth(1000)
        # self.GainLevel=QLabel("0")

        self.VolumeLabel = QLabel("Mic Array Digital Volume :")
        self.VolumeLabel.setFont(BUTTON_FONT)

        self.VolumeFader=QSlider(Qt.Horizontal)
        self.VolumeFader.setMinimum(0)
        self.VolumeFader.setMaximum(24)
        self.VolumeFader.setValue(0)
        self.VolumeFader.setTickPosition(QSlider.TicksBelow)
        self.VolumeFader.valueChanged.connect(self.update_label)
        self.VolumeFader.setTickInterval(1)
        self.VolumeFader.setFont(QFont("Arial",40))
        self.VolumeFader.setStyleSheet(SLIDER_STYLE_2)
        self.VolumeFader.setFixedWidth(1000)
        # self.VolumeLevel=QLabel(str(0))



        self.FilterSelectLabel = QLabel("Mic Array Filter Select     :")
        self.FilterSelectLabel.setFont(BUTTON_FONT)




        self.CheckBox_6kHz = self.Create_RadioBotton('6khz')
        self.CheckBox_6kHz.clicked.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_6K.value))
        self.CheckBox_12kHz = self.Create_RadioBotton('12khz')
        self.CheckBox_12kHz.clicked.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_12K.value))
        self.CheckBox_18kHz = self.Create_RadioBotton('18khz')
        self.CheckBox_18kHz.clicked.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_18K.value))
        self.CheckBox_Full = self.Create_RadioBotton('Full Range')
        self.CheckBox_Full.clicked.connect(lambda:self.ToggleSelection(Frequency_Selection.LPF_FULL.value))

        self.BackButton = QPushButton()
        self.BackButton.clicked.connect(self.switchPage)
        self.BackButton.setFixedSize(NUM_BUTTON_WIDTH+100,NUM_BUTTON_HEIGHT)
        self.BackButton.setText("Back")
        self.BackButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.BackButton.setFont(self.ButtonText)
        self.BackButton.setStyleSheet(BUTTON_STYLE )
        self.BackButton.setFont(QFont("Arial",40))

        self.ApplyButton = QPushButton()
        # self.ApplyButton.clicked.connect(self.switchPage)
        self.ApplyButton.setFixedSize(NUM_BUTTON_WIDTH+100,NUM_BUTTON_HEIGHT)
        self.ApplyButton.setText("Apply")
        self.ApplyButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ApplyButton.setFont(self.ButtonText)
        self.ApplyButton.setStyleSheet(BUTTON_STYLE )
        self.ApplyButton.setFont(QFont("Arial",40))



        self.SettingPage.addWidget(self.GainLabel,1,0)
        self.SettingPage.addWidget(self.GainFader,1,1,1,4)
        # self.SettingPage.addWidget(self.GainLevel,1,2,alignment=Qt.AlignRight)
        self.SettingPage.addWidget(self.VolumeLabel,2,0)
        self.SettingPage.addWidget(self.VolumeFader,2,1,1,4)
        # self.SettingPage.addWidget(self.VolumeLevel,2,2,alignment=Qt.AlignRight)
        self.SettingPage.addWidget(self.FilterSelectLabel,3,0)

        self.SettingPage.addWidget(self.CheckBox_6kHz,3,1)
        self.SettingPage.addWidget(self.CheckBox_12kHz,3,2)
        self.SettingPage.addWidget(self.CheckBox_18kHz,3,3)
        self.SettingPage.addWidget(self.CheckBox_Full,3,4)

        self.SettingPage.addWidget(self.ApplyButton,4,0,1,4,alignment=Qt.AlignRight)
        self.SettingPage.addWidget(self.BackButton,4,1,1,4,alignment=Qt.AlignRight)
        
        
        self.SettingPageWidget = QWidget()
        self.SettingPageWidget.setLayout(self.SettingPage)
        
        self.SettingPageWidget.setFixedSize(1920,1080)
        # self.SettingPageWidget.setGeometry(1920,1080,960,1080)


        self.stacked_widget.setContentsMargins(0,0,0,0)
        self.MainPage.setContentsMargins(0,0,0,0)
        self.layout.setContentsMargins(0,0,0,0)
       
        self.stacked_widget.addWidget(self.MainPageWidget)
        self.stacked_widget.addWidget(self.SettingPageWidget)

        # self.ToggleSelection(Frequency_Selection.LPF_FULL.value)

        # self.stacked_widget.(self.MainPage)
        self.layout.addWidget(self.stacked_widget)
        # self.setContentsMargins(0,0,0,0)
        
        # set the vbox layout as the widgets layout
        self.setLayout(self.layout)
        self.setFixedSize(1920,1080)
 

      
        self.setGeometry(QApplication.screens()[self.ScreenNumber].geometry())
        self.showFullScreen()
        # create the video capture thread
        self.thread = VideoThread()

        self.audio_thread = AudioThread()
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
        i = 0
        list_of_range = [self.CheckBox_6kHz,self.CheckBox_12kHz,self.CheckBox_18kHz,self.CheckBox_Full]
        list_frequency = [Frequency_Selection.LPF_6K,Frequency_Selection.LPF_12K,Frequency_Selection.LPF_18K,Frequency_Selection.LPF_FULL]
        for item in list_frequency:
            if item.value != choice:
                list_of_range[i].setChecked(False)
            else:
                    list_of_range[i].setChecked(True)
            i+=1

    def mousePressEvent(self, event):
        # Handle mouse press events
        mouse_position = event.pos()
        self.text_label.appendPlainText(f"Clicked on [{mouse_position.x()},{mouse_position.y()}]")
        # Add ethernet handler here 
    

    def Create_RadioBotton(self,Title):
        Target = QRadioButton(Title) 
        Target.setGeometry(200, 150, 100, 30) 
        Target.setChecked(False) 
        Target.setFont(BUTTON_FONT)
        Target.setStyleSheet(RADIO_STYLE)
        return Target
    
    def Record_clicked(self):
        self.RECORDING = not self.RECORDING
        if self.RECORDING == True:
            self.RecordButton.setStyleSheet("background-color:red ; color :white ;border-width: 4px;border-radius: 20px;")

            self.text_label.appendPlainText("Recording")
            self.start_recording()
        else:
            self.RecordButton.setStyleSheet(BUTTON_STYLE_RED)
            self.text_label.appendPlainText("Stopped Recording")   
            self.stop_recording
                  
    def update_label(self, value):
        # Update the label text with the current slider value
        print(value)

    def switchPage(self):
        self.index+=1 
        if (self.index > 1 ):
            
            self.index = 0
            
        next_index = self.index % self.stacked_widget.count()  # Cycle through the pages
        self.stacked_widget.setCurrentIndex(next_index)


    def start_recording(self):
        self.is_recording = True
        self.text_label.appendPlainText('Status: Recording')

        self.audio_thread.start()
        # with open(CURRENT_PATH+"/Command.txt", 'w') as file:
        # # Write some text to the file
        #     file.write("Recording")
       

    def stop_recording(self):
        self.is_recording = False
        self.text_label.appendPlainText('Status: Not Recording')
        with open(CURRENT_PATH+"/Command.txt", 'w') as file:
        # Write some text to the file
            file.write("Stop")



    

    def Exit(self):
        exit()
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())