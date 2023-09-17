import time
import threading
import cv2
from buffer import buffer_porcentaje


class Camara(threading.Thread):
    def __init__(self, mqtt_client):
        super().__init__()
        self.daemon = True
        self.stop_event = threading.Event()
        self.buffer = 0
        self.mqtt_client = mqtt_client
        self.metricas = "/metricas/buffer" 
    
    def capturar_foto(self, nombre):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        ret, frame = cap.read()
        cv2.imwrite(nombre, frame)
        cap.release()

    def fin(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            self.capturar_foto("foto_buffer.jpg")
            self.buffer = buffer_porcentaje("foto_buffer.jpg")
            self.mqtt_client.send_metric(self.metricas, self.buffer)
            time.sleep(60)
