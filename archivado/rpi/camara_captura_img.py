from libcamera import PiCamera
from time import sleep

camara = PiCamera()
camara.start_preview()
sleep(5)
camara.capture('/Desktop/joaco.png')
camara.stop_preview()

