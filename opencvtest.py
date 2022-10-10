import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)

if not cap.isOpened():
    raise IOError("Cannot Open Webcam")
    exit()

while True:
    ret, frame = cap.read()
    
    cv.imshow('Input', frame)
    
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv.destroyAllWindows