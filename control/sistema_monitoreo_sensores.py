import time
import RPi.GPIO as GPIO
import numpy as np


class SistemaMonitoreoSensores():
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.ponton = False
        self.contenedores = {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0}
        self.posicion_cinta_cm = 0
        self.posicion_media = { "0": 51, "1": 36, "2": 21.5, "3":5.5 , "4": 56, "5": 40.5, "6": 25 ,"7": 10.3} 
        self.sensor = 0
        self.config()

    def config(self):
        # Modo BCM (figuran en la rpi como GPIOx)
        GPIO.setmode(GPIO.BCM)

        # Ultrasonido ubicacion cinta
        self.trigger_ubi = 7
        self.echo_ubi = 24
        GPIO.setup(self.trigger_ubi, GPIO.OUT)
        GPIO.setup(self.echo_ubi, GPIO.IN)
        
        # Ultrasonido llenado proa ( contenedores nro :4 ,5 ,6 ,7)
        self.trigger_tacho_2 = 14        
        self.echo_tacho_2 = 15
        GPIO.setup(self.trigger_tacho_2, GPIO.OUT)
        GPIO.setup(self.echo_tacho_2, GPIO.IN)

        # Ultrasonido llenado popa ( contenedores nro : 0 ,1 ,2 ,3)
        self.trigger_tacho_1 = 16
        self.echo_tacho_1 = 18
        GPIO.setup(self.trigger_tacho_1, GPIO.OUT)
        GPIO.setup(self.echo_tacho_1, GPIO.IN)
        
        # Velocidad del sonido en cm / s
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
            print("Se detecto el Ponton")
        else:
            value = 0
            print("No se detecto el Ponton")
        self.mqtt_client.send_metric("metricas/ponton", value)
        return self.ponton
    
    def distancia_ultrasonido(self, trigger, echo):
        # Ponemos en bajo el pin TRIG y despues esperamos 0.5 seg para que el transductor se estabilice
        GPIO.output(trigger, GPIO.LOW)
        time.sleep(0.5)
        #Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajo
        GPIO.output(trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trigger, GPIO.LOW)
        
        # Se espera que el sensor emita la señal ultrasónica y el pin ECHO cambie a estado alto
        while True:
            pulso_inicio = time.time()
            if GPIO.input(echo) == GPIO.HIGH:
                break
        # Se espera que la señal ultrasónica regrese y el pin ECHO cambie a estado bajo
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
            distancia = self.distancia_ultrasonido(self.trigger_ubi, self.echo_ubi)
            # Se utiliza para caluclar la distancia cuando la cinta se mueve hacia la proa
            if sentido == True:
                if self.posicion_cinta_cm <  distancia < (self.posicion_cinta_cm + 2.5):
                    return distancia
                else:
                    distancia = None
            else:
                # Se utiliza para caluclar la distancia cuando la cinta se mueve hacia la popa
                if (self.posicion_cinta_cm - 2.5) < distancia < self.posicion_cinta_cm:
                    return distancia
                else:
                    distancia = None
        
    def ubicacion_cinta(self, sentido):  
        self.posicion_cinta_cm = self.medir_ubicacion_cinta(sentido)
        self.mqtt_client.send_metric("metricas/distribucion_pos", self.posicion_cinta)
        self.mqtt_client.send_metric("metricas/distribucion_pos_cm", self.posicion_cinta_cm)

    def medir_ubicacion_cinta_inicial(self):        
        distancia = self.distancia_ultrasonido(self.trigger_ubi, self.echo_ubi)
        print(f"Posicion inicial del la cinta de distrbucion {distancia} cm")
        self.posicion_cinta_cm = distancia

    def medir_llenado_contenedor(self, sensor, tacho):
        aux = self.medir_llenado(sensor)  # cuando tenga los 2 sensores, hay que especificar cual usar
        if aux > self.contenedores[str(tacho)]:
                self.contenedores[str(tacho)] = aux
                topic = "metricas/tacho" + str(tacho)
                self.mqtt_client.send_metric( topic, self.contenedores[str(tacho)])
                print(self.contenedores[str(tacho)])

    def medir_llenado(self, sensor):
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
