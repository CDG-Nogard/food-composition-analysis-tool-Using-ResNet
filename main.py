import cv2
import sys
import requests
import multiprocessing
from multiprocessing import Process
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer, QByteArray
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QDesktopWidget, QTextBrowser

import food_recognition
from after_recognition import getStrNutrients, get_food_info, getStrRecipes

# multithread for avoiding real-time video delay due to processing
def read(que):
    # print("1")
    video_capture = cv2.VideoCapture('rtsp://10.0.0.14') # capture from rtsp stream
    # video_capture = cv2.VideoCapture(0) # Video capture from webcam
    video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) # Set video capture codec

    while video_capture.isOpened():
        ret, img = video_capture.read() # Read video frames
        len = que.qsize() # Get the current size of the queue
        if len>2:
            for i in range(len-2):
                frame = que.get() # Remove excess frames from the queue
        que.put(img) # Put the current frame into the queue

    cv2.destroyAllWindows()
    video_capture.release()

# Create PyQt5 application and window for video playback
def run(que):
    # print("2")
    app = QApplication(sys.argv)
    window = VideoPlayer(que)
    window.show()
    app.exec_()


# user interface design
class VideoPlayer(QMainWindow):
    def __init__(self, que):
        super(VideoPlayer, self).__init__()
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width()/4)
        height = int(screen.height()/4)
        self.setWindowTitle("Food Recognition")
        self.setGeometry(width, height, width*2, height*2)

        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        self.food_label = QLabel()
        self.food_label.setFont(QFont("Helvetica", 12, QFont.Bold)) 
        self.food_label.setAlignment(Qt.AlignCenter)
        self.food_label.setStyleSheet("QLabel { background-color : white; color : red; }")

        self.fps_label = QLabel()
        self.fps_label.setFont(QFont("Helvetica", 12, QFont.Bold)) 
        self.fps_label.setAlignment(Qt.AlignCenter)
        self.fps_label.setStyleSheet("QLabel { background-color : white; color : red; }")

        self.mode_label = QLabel()
        self.mode_label.setFont(QFont("Helvetica", 12, QFont.Bold)) 
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("QLabel { background-color : white; color : red; }")

        self.button1 = QPushButton("Recognization/Camera Mode Switch", self)
        self.button1.setFont(QFont("Helvetica", 12, QFont.Bold)) 
        self.button1.clicked.connect(self.button1_event)

        self.button2 = QPushButton("Pause", self)
        self.button2.setFont(QFont("Helvetica", 12, QFont.Bold)) 
        self.button2.clicked.connect(self.button2_event) 

        self.button3 = QPushButton("Get Food Information", self)
        self.button3.setFont(QFont("Helvetica", 12, QFont.Bold)) 
        self.button3.setEnabled(False)
        self.button3.clicked.connect(self.button3_event) 

        self.button4 = QPushButton("Get Food Recipes", self)
        self.button4.setFont(QFont("Helvetica", 12, QFont.Bold)) 
        self.button4.setEnabled(False)
        self.button4.clicked.connect(self.button4_event) 

        self.layout = QVBoxLayout()

        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(self.mode_label)
        h_layout1.addWidget(self.fps_label)

        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(self.button1)
        h_layout2.addWidget(self.button2)

        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(self.button3)
        h_layout3.addWidget(self.button4)

        self.layout.addLayout(h_layout1)
        self.layout.addWidget(self.food_label)
        self.layout.addWidget(self.label)
        self.layout.addLayout(h_layout2)
        self.layout.addLayout(h_layout3)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.info_window = QMainWindow()
        self.info_window.setGeometry(width, height, width*2, height*2)
        self.info_window.setWindowTitle("Food Information")
        self.info_window.setVisible(False)

        self.food_info_text = QTextBrowser()
        self.food_info_text.setReadOnly(True)
        self.food_info_text.setFont(QFont("Helvetica", 12, QFont.Bold))
        # self.food_info_text.setStyleSheet("QTextBrowser { background-color : white; color : red; }")

        self.food_info_image = QLabel()
        self.food_info_image.setAlignment(Qt.AlignCenter)
        # pixmap = QPixmap("test.jpg")
        # self.food_info_image.setPixmap(pixmap)

        self.info_window.layout = QHBoxLayout()
        self.info_window.layout.addWidget(self.food_info_text)
        self.info_window.layout.addWidget(self.food_info_image)
        
        self.info_window.central_widget = QWidget()
        self.info_window.central_widget.setLayout(self.info_window.layout)
        self.info_window.setCentralWidget(self.info_window.central_widget)

        self.recipe_window = QMainWindow()
        self.recipe_window.setGeometry(width, height, width*2, height*2)
        self.recipe_window.setWindowTitle("Food Information")
        self.recipe_window.setVisible(False)

        self.food_recipe = QTextBrowser()
        self.food_recipe.setReadOnly(True)
        self.food_recipe.setFont(QFont("Helvetica", 12, QFont.Bold))

        self.recipe_window.layout = QHBoxLayout()
        self.recipe_window.layout.addWidget(self.food_recipe)
        
        self.recipe_window.central_widget = QWidget()
        self.recipe_window.central_widget.setLayout(self.recipe_window.layout)
        self.recipe_window.setCentralWidget(self.recipe_window.central_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10) # Update frame every 10ms

        self.que = que
        self.mode = "Camera"
        self.food_name = ""

        self.start_time = cv2.getTickCount()
        self.frame_counter = 0

    def update_frame(self):
        frame = None
        while frame is None:
            if self.que.qsize()==0:
                continue
            frame = self.que.get()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (960, 540), interpolation=cv2.INTER_LINEAR)
        height, width, channel = frame_resized.shape
        bytes_per_line = channel * width
        q_image = QImage(frame_resized.data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        self.label.setPixmap(q_pixmap)

        self.frame_counter += 1
        if self.frame_counter == 30:  # 
            end_time = cv2.getTickCount()
            elapsed_time = (end_time - self.start_time) / cv2.getTickFrequency()
            fps = self.frame_counter / elapsed_time
            self.fps_label.setText(f"FPS: {fps:.2f}")
            self.start_time = cv2.getTickCount()
            self.frame_counter = 0
            if self.mode == "Recognizing":
                self.food_name = food_recognition.recognize(frame_rgb).replace("_", " ")
                self.food_label.setText(f"Name: {self.food_name}")
        self.mode_label.setText(f"Mode: {self.mode}")

    def button1_event(self):
    # Switch between recognition and camera mode
        if self.mode == "Recognizing":
            self.mode = "Camera"
            self.food_label.setText("")
            self.button3.setEnabled(False)
            self.button4.setEnabled(False)
        else:
            self.mode = "Recognizing"
            self.button3.setEnabled(True)
            self.button4.setEnabled(True)

    def button2_event(self):
    # Pause and resume video playback
        if self.timer.isActive():
            self.timer.stop()
            self.mode_label.setText("Mode: Stopped")
            self.button2.setText("Resume")
        else:
            self.timer.start(10)
            self.button2.setText("Pause")
            
    def button3_event(self):
    # Get food information for recognized food
        if self.timer.isActive():
            self.timer.stop()
            self.mode_label.setText("Mode: Stopped")
            self.button2.setText("Resume")
        info_text = str(getStrNutrients(self.food_name))
        # print(info_text)
        self.food_info_text.setPlainText(info_text)
        # self.food_info_text.setHtml(info_text)
        # self.food_info_text.setOpenLinks(True)
        # self.food_info_text.setOpenExternalLinks(True)

        # print(info_text["image_url"])
        response = requests.get(get_food_info(self.food_name)["image_url"])
        image_data = response.content
        pixmap = QPixmap() 
        pixmap.loadFromData(QByteArray(image_data))
        screen = QDesktopWidget().screenGeometry()
        scaled_pixmap = pixmap.scaledToWidth(int(screen.width()/4))
        self.food_info_image.setPixmap(scaled_pixmap)

        self.info_window.setVisible(True)

    def button4_event(self):
    # Get food recipes for recognized food
        if self.timer.isActive():
            self.timer.stop()
            self.mode_label.setText("Mode: Stopped")
            self.button2.setText("Resume")
        
        info_text = getStrRecipes(self.food_name)
        # print(info_text)
        self.food_recipe.setHtml(info_text)
        self.food_recipe.setOpenLinks(True)
        self.food_recipe.setOpenExternalLinks(True)
        

        self.recipe_window.setVisible(True)

if __name__ == "__main__":

    manager = multiprocessing.Manager()
    que = manager.Queue()

    p1 = Process(target=read,args=(que,))
    p1.start()
    
    p2 = Process(target=run, args=(que,))
    p2.start()

    p2.join()
    p1.terminate()
    p1.join()