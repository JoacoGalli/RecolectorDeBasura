import time
import threading
from RpiMotorLib import RpiMotorLib as motor
import RPi.GPIO as GPIO
from new_buffer import buffer_porcentaje
from mqtt_influx_class import MQTTClient
import numpy as np
import cv2
import subprocess

# from sensores import medir_si_esta_ponton, medir_ubicacion_cinta, mover_cinta_traslacion, medir_buffer, activar_motores_rotacion, reset_motores_rotacion


class Maquina_del_mal():
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.ponton = False
        self.cant_tachos = 8
        self.contenedores = {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0}
        self.buffer = None
        self.posicion_cinta = None # 1 2 3 4        
        self.posicion_cinta_cm = 0
        self.sensor = 0
        self.posicion_media = { "0": 51, "1": 36, "2": 21.5, "3":5.5 , "4": 56, "5": 40.5, "6": 25 ,"7": 10.3} 
        self.set_maquina()

    def set_maquina(self):
        # ultrasonido ubicacion cinta
        GPIO.setmode(GPIO.BCM)
        self.trigger_ubi = 7
        self.echo_ubi = 24
        GPIO.setup(self.trigger_ubi, GPIO.OUT)
        GPIO.setup(self.echo_ubi, GPIO.IN)
        
        # ultrasonido llenado trasero 
        self.trigger_tacho_2 = 14        
        self.echo_tacho_2 = 15
        GPIO.setup(self.trigger_tacho_2, GPIO.OUT)
        GPIO.setup(self.echo_tacho_2, GPIO.IN)

        # ultrasonido llenado delantero
        self.trigger_tacho_1 = 16
        self.echo_tacho_1 = 18
        GPIO.setup(self.trigger_tacho_1, GPIO.OUT)
        GPIO.setup(self.echo_tacho_1, GPIO.IN)
        
        self.sound_speed = 34300

        # IR
        self.sensor_ir = 21
        GPIO.setup(self.sensor_ir, GPIO.IN)

    def medir_si_esta_ponton(self):
        ti = time.time()
        tf = time.time()
        while (tf - ti < 1):
            if (not GPIO.input(self.sensor_ir)):
                ponton = True
                while GPIO.input(self.sensor_ir):
                    time.sleep(0.2)
            else:
                ponton = False
            tf = time.time()
        if ponton:
            print("Se detecto el Ponton")
        else:
            print("No se detecto el Ponton")

        return ponton

    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        if self.ponton:
            value = 1
        else:
            value = 0
        self.mqtt_client.send_metric("metricas/ponton", value)
        return self.ponton
    
    def distancia_ultrasonido(self, trigger, echo):
            GPIO.output(trigger, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(trigger, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(trigger, GPIO.LOW)

            while True:
                pulso_inicio = time.time()
                if GPIO.input(echo) == GPIO.HIGH:
                    break

            while True:
                pulso_fin = time.time()
                if GPIO.input(echo) == GPIO.LOW:
                    break

            # Tiempo medido en segundos
            duracion = pulso_fin - pulso_inicio

            # Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
            distancia = (self.sound_speed * duracion) / 2
            return distancia
        


    def medir_ubicacion_cinta(self, sentido):
        distancia = None
        while distancia == None:
            distancia = self.distancia_ultrasonido(self.trigger_ubi, self.echo_ubi)
            print(f"{distancia=}")
            if sentido == True:
                if self.posicion_cinta_cm <  distancia < (self.posicion_cinta_cm + 2.5):
                    return distancia
                else:
                    distancia = None
            else:
                if (self.posicion_cinta_cm - 2.5) < distancia < self.posicion_cinta_cm:
                    #self.mqtt_client.send_metric(self.metricas, distancia)
                    return distancia
                else:
                    distancia = None
        

    def ubicacion_cinta(self, sentido):  
        self.posicion_cinta_cm = self.medir_ubicacion_cinta(sentido)
        
        self.mqtt_client.send_metric(
            "metricas/distribucion_pos", self.posicion_cinta)
        self.mqtt_client.send_metric(
            "metricas/distribucion_pos_cm", self.posicion_cinta_cm)

    def medir_ubicacion_cinta_inicial(self):        
            distancia = self.distancia_ultrasonido(self.trigger_ubi, self.echo_ubi)
            print(f"Posicion inicial del la cinta de distrbucion {distancia} cm")
            self.posicion_cinta_cm = distancia

    def medir_llenado_tachos(self, sensor, tacho):
        aux = self.medir_llenado(sensor)  # cuando tenga los 2 sensores, hay que especificar cual usar
        if aux > self.contenedores[str(tacho)]:
                self.contenedores[str(tacho)] = aux
                topic = "metricas/tacho" + str(tacho)
                self.mqtt_client.send_metric( topic, self.contenedores[str(tacho)])
                print(self.contenedores[str(tacho)])

    
    def medir_llenado(self, sensor):
        #trigger = self.trigger_tacho_1
        #echo = self.echo_tacho_1
        if sensor == 2:
                trigger = self.trigger_tacho_2
                echo = self.echo_tacho_2
                distancia_vacio = 10.5
                distancia_lleno = 1.5
        elif sensor == 1:
                trigger = self.trigger_tacho_1
                echo = self.echo_tacho_1
                distancia_vacio = 12
                distancia_lleno = 5 
        else:
                trigger =None
                echo = None
                print("No voy a medir nada")
        
        list_dist = []
        for x in range(7):    
                distancia = self.distancia_ultrasonido(trigger, echo)
                if distancia > distancia_vacio :
                    pass
                else:
                    list_dist.append(distancia)

        if list_dist:
            distancias_filtradas = np.mean(list_dist)
            porcentaje = (distancia_vacio - distancias_filtradas) * 100 / (distancia_vacio - distancia_lleno)
            print(f'estas son las {distancias_filtradas=}')
            return porcentaje
        return 0

class Motores_traslacion(threading.Thread):

    def __init__(self, mqtt):
        threading.Thread.__init__(self)
        self.mqtt_client = mqtt
        self.deamon = True
        self.motores_status = 'off' # on, off, reset
        self.config()
        self.stop_event = threading.Event()

    def config(self):
        # motor
        self.direcction = 17
        self.step = 27
        self.cw = 1
        self.ccw = 0
        self.clockwise = False
        self.step_type = "Full"
        self.steps = 100
        self.velocidades = [0.025,0.02, 0.009, 0.008, 0.007]
        self.velocidad = 1
        self.verbose = False
        self.init_delay = 0.01
        self.metricas = "metricas/motor_traslacion"
        self.mode_pin = (-1, -1, -1)
        self.motor_traslacion_nema = motor.A4988Nema(
            self.direcction, self.step, self.mode_pin, "A4988")
        #self.reset_motores_traslacion()
    def activar_motores_traslacion(self):
        while self.motores_status == 'on':
            self.mqtt_client.send_metric(self.metricas, 1)
            self.mqtt_client.send_metric(self.metricas+"_vel", self.velocidad)
            self.motor_traslacion_nema.motor_go(
                self.clockwise, self.step_type, self.steps, self.velocidades[self.velocidad], self.verbose, self.init_delay)

    def reset_motores_traslacion(self):
        self.motor_traslacion_nema.motor_stop()

    def fin(self):
        self.motores_status = "off" 
        self.reset_motores_traslacion()
        self.stop_event.set()

    def run(self):
        cont = 0
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                cont = 0
                self.activar_motores_traslacion()
            elif self.motores_status == 'off':
                if cont == 0:
                    self.reset_motores_traslacion()
                    self.mqtt_client.send_metric(self.metricas, 0)
                    self.mqtt_client.send_metric(self.metricas + "_vel",self.velocidad)
                cont += 1
                time.sleep(0.1)
            else:
                pass


class Motores_rotacion(threading.Thread):
    def __init__(self, mqtt, tipo, camara):
        threading.Thread.__init__(self)
        self.mqtt_client = mqtt
        self.deamon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = 0 #en 1 por que solo nos interesa que gire en ese sentido #None # "right" "left"
        self.stop_event = threading.Event()
        self.velocidades = [0.01, 0.009, 0.008, 0.007]
        self.velocidad = 0
        self.tipo = tipo
        self.metricas = "metricas/"
        self.camara = camara
        self.config()
        
    def config(self):
        if self.tipo == "dist":
            self.dir = 5 
            self.step = 6 
            self.velocidad = 0
            self.metricas += "motor_rotacion_dist"
        elif self.tipo == "cap":
            self.dir = 26 
            self.step = 19 
            self.velocidad = 0
            self.sentido = 1
            self.metricas += "motor_rotacion_cap"
        else:
            print("No hay ningun motor para setear.")
        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)


        # Set the first direction you want it to spin
        #GPIO.output(self.dir, self.sentido)

    def activar_motores_rotacion(self):
        GPIO.output(self.dir,self.sentido)
        
        if  0 < self.camara < 30:
            self.velocidad = 0

        elif  30 < self.camara < 50:
            self.velocidad = 1
        elif  50 < self.camara < 80:
            self.velocidad = 2
        elif  80 < self.camara < 100:
            self.velocidad = 3
        #self.velocidad = 3

        self.mqtt_client.send_metric(self.metricas, 1)
        self.mqtt_client.send_metric(
            self.metricas + "_vel", self.velocidad)
        while self.motores_status == "on":
            # Run for 200 steps. This will change based on how you set you controller
            # Set one coil winding to high
            GPIO.output(self.step,GPIO.HIGH)
            # Allow it to get there.
            time.sleep(self.velocidades[self.velocidad]) # Dictates how fast stepper motor will run
            # Set coil winding to low
            GPIO.output(self.step,GPIO.LOW)
            time.sleep(self.velocidades[self.velocidad]) # Dictates how fast stepper motor will run
    
    def fin(self):
        self.motores_status = "off"
        self.stop_event.set()
    
    def run(self):
        cont = 0
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                cont = 0
                self.activar_motores_rotacion()
            elif self.motores_status == 'off':
                if cont == 0:
                    self.mqtt_client.send_metric(self.metricas, 0)
                    self.mqtt_client.send_metric(self.metricas + "_vel", self.velocidad)
                cont +=1
                time.sleep(0.5)
            else:
                pass         
                
                
            
class Camara(threading.Thread):
    def __init__(self, mqtt):
        super().__init__()
        self.daemon = True
        self.stop_event = threading.Event()
        self.buffer = 2
        self.mqtt_client = mqtt
        self.metricas = "metricas/" 
    
    def tomar_foto(self, nombre):
        subprocess.run(["python", "capturar_foto.py", nombre])  # Pasar el nombre de archivo como argumento
        #cap = cv2.VideoCapture(0)
        #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        #ret, frame = cap.read()
        #print("saque la foto")
        #cv2.imwrite(nombre, frame)
        #cap.release()

    def fin(self):
        self.stop_event.set()

    def run(self):
        count = 0
        valor = [30, 40, 60, 70, 50, 80, 25, 64, 83, 47, 77, 58, 62, 91, 70, 64, 72, 87, 95, 77, 55, 64, 70, 75 ]*2
        while not self.stop_event.is_set():
            n = str(count)
            self.bufffer = valor[count] 
            #self.tomar_foto("foto_buffer_"+n+".jpg")
            #self.buffer = buffer_porcentaje("foto_buffer_"+n+".jpg")
            self.mqtt_client.send_metric(
            self.metricas + "buffer", self.buffer)
            #print('envie metricas')
            count += 1
            time.sleep(75)

if __name__ == "__main__2":
    n = "n"
    motor = Motores_traslacion(n)
    motor.start()
    print("arranque")
    time.sleep(1)
    motor.velocidad = 0
    motor.clockwise = True
    motor.motores_status = "on"
    time.sleep(8)
    motor.motores_status = "off"
    time.sleep(1)
    motor.clockwise = True
    motor.motores_status = "on"
    time.sleep(8)
    motor.motores_status = "off"
    motor.fin()

if __name__ == "__main__":
    mqtt_client = MQTTClient()
    for x in range(100):
        mqtt_client.send_metric("/metricas/buffer", x)
        print(x)
        time.sleep(2)
    #cam.start()
    #time.sleep(300)
