#from picamera import PiCamera
#from time import sleep

#camera = PiCamera()

#camera.start_preview()
#sleep(60)
#camera.stop_preview()

import cv2
print(cv2.__file__)

capture = cv2.VideoCapture(0)
 
while(True):
     
    ret, frame = capture.read()
     
    cv2.imshow('video', frame)
     
    if cv2.waitKey(1) == 27:
        break
 
capture.release()
cv2.destroyAllWindows()