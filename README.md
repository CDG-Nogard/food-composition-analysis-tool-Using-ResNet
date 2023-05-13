# food-composition-analysis-tool-Using-ResNet

Environment: Python 3.11.2

Required third-party libraries:
beautifulsoup4           4.12.2
bs4                      0.0.1
matplotlib               3.7.1
numpy                    1.24.2
opencv-python            4.7.0.68
Pillow                   9.4.0
PyQt5                    5.15.9
PyQt5-Qt5                5.15.2
PyQt5-sip                12.11.1
pywin32                  305
requests                 2.28.2
torch                    2.0.0
torchvision              0.15.1
Wikipedia-API            0.5.8

Label file: food_labels.txt;
Model file: model.pth;
Check if the two files are in the directory,
and then you can directly run the main.py, which display the User interface.

Directly run food_recognition.py. It will read the test.jpg in the directory and recognize it. 
The output will be printed on terminal.

Directly run after_recognition.py. It will query information of "Banana"(you can change it) from several food API.
The output will also be printed on terminal.

Directly run Camera_test.py. But you need a rtsp address to see the video stream.

Directly run get_pre_trained.py. You will get "resnet50_food.pth" model file in directory.

Before run train.py, you should first download the dataset from https://www.kaggle.com/datasets/muhriddinmuxiddinov/fruits-and-vegetables-dataset?resource=download.
Check the folder path, and modify the source path and target path in preprocess.py.
Then you modify the path in train.py to use the separated train set and valid set for training.
The model will be stored in file called "finalmodel.pth". 
