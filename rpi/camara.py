from picamera.array import PiRGBArray
from picamera import PiCamera
import time, cv2, subprocess

with PiCamera() as camera:
    capImg = PiRGBArray(camera)
    time.sleep(0.1)
    camera.capture(capImg, format='bgr')
    image = capImg.array
    cv2.imwrite('image1.bmp',image)
