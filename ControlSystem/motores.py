import time
import threading
from RpiMotorLib import RpiMotorLib as motor
import RPi.GPIO as GPIO


class MotorTraslacion(threading.Thread):

    def __init__(self, mqtt):
        threading.Thread.__init__(self)
        self.mqtt_client = mqtt
        self.deamon = True
        self.stop_event = threading.Event()

        self.estado = 'off'
        self.config()
        
    def config(self):
        # Pines
        self.dir = 17
        self.step = 27

        # Configuraciones iniciales.
        self.sentido_horario = False
        self.tipo_paso = "Full"
        self.pasos = 100
        self.velocidades = [0.01, 0.009, 0.008, 0.007]
        self.velocidad = 0
        self.verbose = False
        self.delay_inicial = 0.01
        self.modo = (-1, -1, -1)

        # Configuracion del motor
        self.motor_traslacion_nema = motor.A4988Nema(self.dir, self.step, self.modo, "A4988")
        self.metricas = "metricas/motor_traslacion"

    def activar(self):
        while self.estado == 'on':
            # Se envian metricas de velocidad Y encendido.
            self.mqtt_client.send_metric(self.metricas, 1)
            self.mqtt_client.send_metric(self.metricas+"_vel", self.velocidad)
            # Motor en funcionamiento.
            self.motor_traslacion_nema.motor_go(
                self.sentido_horario, self.tipo_paso, self.pasos, self.velocidades[self.velocidad], self.verbose, self.delay_inicial)

    def reset(self):
        self.motor_traslacion_nema.motor_stop()

    def fin(self):
        self.reset_motores_traslacion()
        self.stop_event.set()

    def run(self):
        cont = 0
        while not self.stop_event.is_set():
            if self.estado == 'on':
                cont = 0
                self.activar()
            elif self.estado == 'off':
                if cont == 0:
                    self.reset()
                    self.mqtt_client.send_metric(self.metricas, 0)
                    self.mqtt_client.send_metric(self.metricas + "_vel",self.velocidad)
                cont += 1
            else:
                pass


class MotorRotacion(threading.Thread):
    def __init__(self, mqtt, motor, camara):
        threading.Thread.__init__(self)
        self.mqtt_client = mqtt
        self.deamon = True
        self.stop_event = threading.Event()

        self.estado = "off"
        self.sentido_horario = False
        self.velocidades = [0.01, 0.009, 0.008, 0.007]
        self.velocidad = 0
        # Se configura el motor de captacion o el de distribucion.
        self.motor = motor 
       
        # Esta clase recibe la camara ya que debe usar el % del buffer para setear la velocidad.
        self.camara = camara
        self.metricas = "metricas/"
        self.config()
        
    def config(self):
        if self.motor == "dist":
            self.dir = 5 
            self.step = 6 
            self.velocidad = 0
            self.metricas += "motor_rotacion_dist"
        elif self.motor == "cap":
            self.dir = 26 
            self.step = 19 
            self.velocidad = 0
            self.sentido_horario= 1
            self.metricas += "motor_rotacion_cap"
        else:
            print("No hay ningun motor para setear.")
        
        # Se configura el modo y los pines de salida
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)


    def activar(self):
        # Se configura la direccion de rotacion
        GPIO.output(self.dir, self.sentido_horario)
        
        # Con respecto al % de llenado del buffer se setea la velocidad del motor
        if  0 < self.camara < 30:
            self.velocidad = 0
        elif  30 < self.camara < 50:
            self.velocidad = 1
        elif  50 < self.camara < 80:
            self.velocidad = 2
        elif  80 < self.camara < 100:
            self.velocidad = 3

        self.mqtt_client.send_metric(self.metricas, 1)
        self.mqtt_client.send_metric(self.metricas + "_vel", self.velocidad)

        while self.estado == "on":
            GPIO.output(self.step, GPIO.HIGH)
            time.sleep(self.velocidades[self.velocidad])
            GPIO.output(self.step, GPIO.LOW)
            time.sleep(self.velocidades[self.velocidad])
    
    def fin(self):
        self.stop_event.set()
    
    def run(self):
        cont = 0
        while not self.stop_event.is_set():
            if self.estado == 'on':
                cont = 0
                self.activar()
            elif self.estado == 'off':
                if cont == 0:
                    print("envio las metricas de apagado 1 vez")
                    self.mqtt_client.send_metric(self.metricas, 0)
                    self.mqtt_client.send_metric(self.metricas + "_vel", self.velocidad)
                    cont +=1
            else:
                pass         
