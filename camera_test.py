import cv2

# test to open the camera
# cap = cv2.VideoCapture(0)

# try the rtmp stream of IP camera
cap = cv2.VideoCapture('rtsp://10.0.0.169')
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

# print(cap.isOpened())

# cap.set(propId, value)
# cap.set(3, 960)
# cap.set(4, 540)

while cap.isOpened():
    ret_flag, img_camera = cap.read()

    # print("height: ", img_camera.shape[0])
    # print("width:  ", img_camera.shape[1])
    # print('')

    cv2.imshow("camera", img_camera)

    k = cv2.waitKey(1)
    if k == 27: # press esc
        break

cap.release()
cv2.destroyAllWindows()
