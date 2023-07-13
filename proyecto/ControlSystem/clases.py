import time
import threading
from RpiMotorLib import RpiMotorLib as motor
import RPi.GPIO as GPIO
from new_buffer import buffer_porcentaje
from mqtt_influx_class import MQTTClient
import numpy as np


class Maquina_del_mal():
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.ponton = False
        self.contenedores = {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0}     
        self.posicion_cinta_cm = 0
        self.sensor = 0
        # Posiciones en las que la cinta va a ubicar para hacer mediciones en cada contenedor
        self.posicion_media = { "0": 10.5, "1": 24.5, "2": 40.5, "3":53 , "4": 6, "5": 22.5 , "6": 38.7 ,"7": 51.5} 
        self.config()

    def config(self):
        # Modo BCM (figuran en la rpi como GPIOx)
        GPIO.setmode(GPIO.BCM)

        # Ultrasonido ubicacion cinta
        self.trigger_ubi = 7
        self.echo_ubi = 24
        GPIO.setup(self.trigger_ubi, GPIO.OUT)
        GPIO.setup(self.echo_ubi, GPIO.IN)
        
        # Ultrasonido llenado proa (contenedores nro:4,5,6,7)
        self.trigger_contenedor_2 = 14        
        self.echo_contenedor_2 = 15
        GPIO.setup(self.trigger_contenedor_2, GPIO.OUT)
        GPIO.setup(self.echo_contenedor_2, GPIO.IN)

        # Ultrasonido llenado popa (contenedores nro: 0,1,2,3)
        self.trigger_contenedor_1 = 16
        self.echo_contenedor_1 = 18
        GPIO.setup(self.trigger_contenedor_1, GPIO.OUT)
        GPIO.setup(self.echo_contenedor_1, GPIO.IN)
        
        # Velocidad del sonido en cm/s
        self.vel_sonido = 34300

        # IR
        self.sensor_ir = 21
        GPIO.setup(self.sensor_ir, GPIO.IN)

    def deteccion_ir(self):
        ti = time.time()
        tf = time.time()
        while (tf - ti < 1):
            if (not GPIO.input(self.sensor_ir)):
                objeto = True
                while GPIO.input(self.sensor_ir):
                    time.sleep(0.2)
            else:
                objeto = False
            tf = time.time()
        return objeto


    def deteccion_ponton(self):
        self.ponton = self.deteccion_ir()
        if self.ponton:
            value = 1
            print("Pontón ingresado.")
        else:
            value = 0
            print("Pontón retirado.")
        self.mqtt_client.send_metric("metricas/ponton", value)
        return self.ponton
    
    def distancia_ultrasonido(self, trigger, echo):
        # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
        GPIO.output(trigger, GPIO.LOW)
        time.sleep(0.5)
        #Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajo
        GPIO.output(trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trigger, GPIO.LOW)

        # En este momento el sensor envía 8 pulsos ultrasónicos de 40kHz y coloca su pin ECHO en alto
        # Debemos detectar dicho evento para iniciar la medición del tiempo
        while True:
            pulso_inicio = time.time()
            if GPIO.input(echo) == GPIO.HIGH:
                break

        # El pin ECHO se mantendrá en HIGH hasta recibir el eco rebotado por el obstáculo. 
        # En ese momento el sensor pondrá el pin ECHO en bajo.
        # Prodedemos a detectar dicho evento para terminar la medición del tiempo
        while True:
            pulso_fin = time.time()
            if GPIO.input(echo) == GPIO.LOW:
                break

        # Tiempo medido en segundos
        duracion = pulso_fin - pulso_inicio

        # Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
        distancia = (self.vel_sonido * duracion) / 2
        return distancia
    

    def medir_ubicacion_cinta(self, sentido):
        distancia = None
        while distancia == None:
            distancia = self.distancia_ultrasonido(self.trigger_ubi,self.echo_ubi)
            
            # Se utiliza para calcular la distancia inicial de la cinta de distribucion
            if sentido == None:
                self.posicion_cinta_cm = distancia

            # Se utiliza para caluclar la distancia cuando la cinta se mueve hacia la proa
            elif sentido == 1:
                if (self.posicion_cinta_cm - 3) < distancia < self.posicion_cinta_cm:
                    return distancia
                else:
                    distancia = None

            # Se utiliza para caluclar la distancia cuando la cinta se mueve hacia la popa
            elif sentido == 0:
                if self.posicion_cinta_cm <  distancia < (self.posicion_cinta_cm + 3):
                    return distancia
                else:
                    distancia = None

    def ubicacion_cinta(self, sentido):  
        self.posicion_cinta_cm = self.medir_ubicacion_cinta(sentido)
        self.mqtt_client.send_metric("metricas/distribucion_pos", self.posicion_cinta)
        self.mqtt_client.send_metric("metricas/distribucion_pos_cm", self.posicion_cinta_cm)


    def medir_llenado_contenedor(self, sensor, contenedor):
        if sensor == 1:
            aux = self.medir_llenado(sensor)  # cuando tenga los 2 sensores, hay que especificar cual usar
            if aux > self.contenedores[str(contenedor)]:
                    self.contenedores[str(contenedor)] = aux
                    topic = "metricas/tacho" + str(contenedor)
                    self.mqtt_client.send_metric( topic, self.contenedores[str(contenedor)])
                    print(self.contenedores[str(contenedor)])
        if sensor == 2:
            aux = self.medir_llenado(sensor)  # cuando tenga los 2 sensores, hay que especificar cual usar
            if aux > self.contenedores[str(contenedor)]:
                    self.contenedores[str(contenedor)] = aux
                    topic = "metricas/tacho" + str(contenedor)
                    self.mqtt_client.send_metric( topic, self.contenedores[str(contenedor)])
                    print(self.contenedores[str(contenedor)])
    
    def medir_llenado(self, sensor):
        # Ultrasonido llenado proa (contenedores nro:4,5,6,7)
        if sensor == 2:
                trigger = self.trigger_contenedor_2
                echo = self.echo_contenedor_2
                distancia_vacio = 10.5
                distancia_lleno = 1.5
        # Ultrasonido llenado popa (contenedores nro:0,1,2,3)
        elif sensor == 1:
                trigger = self.trigger_contenedor_1
                echo = self.echo_contenedor_1
                distancia_vacio = 14.5
                distancia_lleno = 2
        else:
                trigger =None
                echo = None
                print("No voy a medir nada")
        
        list_dist = []
        # Para una medicion mas precisa, se hace un promedio de 10 muestras y se envia el resultado
        for x in range(10):
                # Ojoo lo unico diferente es que antes se esperaba 0.3s para que estabilice y ahora es 0.5
                distancia = self.distancia_ultrasonido(trigger, echo)
                if distancia > distancia_vacio :
                    pass
                else:
                    list_dist.append(distancia)

        if list_dist:
            distancias_filtradas = np.mean(list_dist)
            porcentaje = (distancia_vacio - distancias_filtradas) * 100 / (distancia_vacio - distancia_lleno)
            return porcentaje
        return 0

class Motores_traslacion(threading.Thread):

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

    def activar_motores_traslacion(self):
        while self.estado == 'on':
            #-----------------
            # Hace falta que este este sleep??
            #-----------------
            time.sleep(0.01)
            # Se envian metricas de velocidad Y encendido.
            self.mqtt_client.send_metric(self.metricas, 1)
            self.mqtt_client.send_metric(self.metricas+"_vel", self.velocidad)
            # Motor en funcionamiento.
            self.motor_traslacion_nema.motor_go(
                self.sentido_horario, self.tipo_paso, self.pasos, self.velocidades[self.velocidad], self.verbose, self.delay_inicial)

    def reset_motores_traslacion(self):
        self.motor_traslacion_nema.motor_stop()

    def fin(self):
        self.reset_motores_traslacion()
        self.stop_event.set()

    def run(self):
        cont = 0
        while not self.stop_event.is_set():
            if self.estado == 'on':
                cont = 0
                self.activar_motores_traslacion()
            elif self.estado == 'off':
                if cont == 0:
                    self.reset_motores_traslacion()
                    self.mqtt_client.send_metric(self.metricas, 0)
                    self.mqtt_client.send_metric(self.metricas + "_vel",self.velocidad)
                    cont += 1
                #-------------
                # El cont lo puse dentro del if == 0, no tenia sentido si no, nunca aumentaba.
                #-------------
            else:
                pass


class Motores_rotacion(threading.Thread):
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


    def activar_motores_rotacion(self):
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
                self.activar_motores_rotacion()
            elif self.estado == 'off':
                if cont == 0:
                    print("envio las metricas de apagado 1 vez")
                    self.mqtt_client.send_metric(self.metricas, 0)
                    self.mqtt_client.send_metric(self.metricas + "_vel", self.velocidad)
                    cont +=1
            else:
                pass         
                
                
class Camara(threading.Thread):
    def __init__(self, mqtt_client):
        super().__init__()
        self.daemon = True
        self.stop_event = threading.Event()
        self.buffer = 0
        self.mqtt_client = mqtt_client
        self.metricas = "/metricas/buffer" 
    
    def tomar_foto(nombre):
        pass

    def fin(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            # --------------------------
            # Falta la funcion que esta en el escritorio de la RPI para sacar fotos
            # --------------------------
            self.tomar_foto("foto_buffer.jpg")
            self.buffer = buffer_porcentaje("foto_buffer.jpg")
            self.mqtt_client.send_metric(self.metricas, self.buffer)
            time.sleep(60)
