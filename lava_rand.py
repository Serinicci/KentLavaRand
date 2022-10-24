import cv2
import numpy as np
from multiprocessing import Process, Queue
import queue
from datetime import datetime

def rgb2tuple(rgb: int):
    return rgb>>16, (rgb>>8)&255, rgb&255

# lamp format (name, left edge, top edge, width, height, min_colour, max_colour)
lamps = [
    ("Lamp 1", 260, 105, 140, 225, rgb2tuple(0x7F3F3F), rgb2tuple(0xFFCFCF))
]
blob_min_size = 100

def cameraProc(q):
    cam = cv2.VideoCapture(0)
    
    cam.set(3,640)
    cam.set(4,480)
    
    cv2.startWindowThread()
    cv2.namedWindow("output")

    while True:
        
        success, img = cam.read()
        if not success:
            break
        
        q.put(img) # send a copy to the rand process
        
        outputImg = img.copy()
        
        for name, left, top, width, height, min_colour, max_colour in lamps:
            cv2.rectangle(img, (left,top), (left+width,top+height), (255,255,255),3)
            cropped = img[top:top+height, left:left+width]
            masked = cv2.inRange(cropped, min_colour, max_colour)
            del cropped
            cv2.putText(outputImg, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            cv2.rectangle(outputImg, (left,top), (left+width,top+height), (0,0,255), 1)
            try:
                contours, heir = cv2.findContours(masked, cv2.RETR_TREE, 1)
                del masked
                for contour in contours:
                    x,y,w,h = cv2.boundingRect(contour)
                    if w*h > blob_min_size:
                        cv2.rectangle(outputImg, (left+x,top+y), (left+x+w,top+y+h), (0,255,0), 1)
                del contours
            except(ValueError, ZeroDivisionError) as e:
                pass
        
        rng = hex(abs(hash((img.data.tobytes(), datetime.now()))))
        cv2.putText(outputImg, rng, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        
        cv2.imshow("output", outputImg)
        
        if cv2.waitKey(10) == ord('q'):
            break
    
    cv2.destroyAllWindows()



def randProc(q):
    return
    while True:
        img = None
        try:
            a = q.get(False,500)
            a.flags.writeable = False
            img = a.data.tobytes()
            print("New img")
        except queue.Empty:
            print("Re-using prev img")
            pass
        except Exception as e:
            print(e)
        val = abs(hash((img, datetime.now())))
        print(hex(val))



if __name__ == "__main__":
    
#     cam = cv2.VideoCapture(0)
#     
#     cam.set(3,640)
#     cam.set(4,480)
#     
#     success, img = cam.read()
#     
#     if success:
#         
#         outputImg = img.copy()
#         
#         for left, top, width, height, min_colour, max_colour in lamps:
#             cv2.rectangle(img, (left,top), (left+width,top+height), (255,255,255),3)
#             cropped = img[top:top+height, left:left+width]
#             masked = cv2.inRange(cropped, rgb2tuple(min_colour), rgb2tuple(max_colour))
#             del cropped
# #             cv2.imshow("masked", masked)
#             cv2.rectangle(outputImg, (left,top), (left+width,top+height), (0,0,255), 1)
#             try:
#                 contours, heir = cv2.findContours(masked, cv2.RETR_TREE, 1)
#                 del masked
#                 for contour in contours:
#                     x,y,w,h = cv2.boundingRect(contour)
#                     if w*h > blob_min_size:
#                         cv2.rectangle(outputImg, (left+x,top+y), (left+x+w,top+y+h), (0,255,0), 1)
#                 del contours
#             except(ValueError, ZeroDivisionError) as e:
#                 pass
#             
#         cv2.imshow("img", outputImg)
#         del img
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
    
    q = Queue()
    proc_funcs = [cameraProc, randProc]
    processes = [Process(target=func, args=(q,)) for func in proc_funcs]
    
    for proc in processes:
        proc.start()
    
    for proc in processes:
        proc.join()