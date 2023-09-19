import time
import threading
from buffer import buffer_porcentaje
import cv2
import subprocess


class Camara(threading.Thread):
    def __init__(self, mqtt):
        super().__init__()
        self.daemon = True
        self.stop_event = threading.Event()
        self.buffer = 2
        self.mqtt_client = mqtt
        self.metricas = "metricas/" 
    
    def tomar_foto(self, nombre):
        #subprocess.run(["python", "capturar_foto.py", nombre])  # Pasar el nombre de archivo como argumento
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        ret, frame = cap.read()
        cv2.imwrite(nombre, frame)
        cap.release()

    def fin(self):
        self.stop_event.set()

    def run(self):
        count = 0
        while not self.stop_event.is_set():
            n = str(count)
            self.tomar_foto("foto_buffer_"+n+".jpg")
            self.buffer = buffer_porcentaje("foto_buffer_"+n+".jpg")
            self.mqtt_client.send_metric(self.metricas + "buffer", self.buffer)
            count += 1
            time.sleep(75)
