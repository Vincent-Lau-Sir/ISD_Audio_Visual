import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sounddevice as sd


from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
import sounddevice as sd

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                self.change_pixmap_signal.emit(frame)

class AudioThread(QThread):
    def run(self):
        sample_rate = 44100  # Hz
        duration = 10  # seconds

        # Use a callback function for non-blocking audio recording
        def callback(indata, frames, time, status):
            if status:
                print(status)
            print("Recording audio...")

        with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
            self.sleep(duration)

class AudioRecorder(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Audio Recorder with Video Display')
        self.setGeometry(100, 100, 800, 600)

        self.record_button = QPushButton('Record', self)
        self.record_button.clicked.connect(self.toggle_recording)

        self.status_label = QLabel('Status: Not Recording', self)
        self.status_label.setAlignment(Qt.AlignCenter)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.record_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.video_label)

        self.is_recording = False
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_video_frame)
        self.video_thread.start()

        self.audio_thread = AudioThread()

        # Use QTimer for UI updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video)
        self.timer.start(30)  # Adjust the interval based on your preference

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.status_label.setText('Status: Recording')
        self.record_button.setText('Stop Recording')

        # Start audio recording in a separate thread
        self.audio_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.status_label.setText('Status: Not Recording')
        self.record_button.setText('Record')

    def update_video(self):
        # Update video frame at regular intervals
        frame = self.video_thread.current_frame
        if frame is not None:
            qt_img = self.convert_cv_qt(frame)
            self.video_label.setPixmap(qt_img)

    def update_video_frame(self, frame):
        self.video_thread.current_frame = frame

    def convert_cv_qt(self, cv_img):
        # Convert OpenCV image to QPixmap
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioRecorder()
    window.show()
    sys.exit(app.exec_())
