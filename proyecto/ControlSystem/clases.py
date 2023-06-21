import time
import threading
from RpiMotorLib import RpiMotorLib as motor
import RPi.GPIO as GPIO
from statistics import mean
from new_buffer import buffer_porcentaje
import numpy as np

# from sensores import medir_si_esta_ponton, medir_ubicacion_cinta, mover_cinta_traslacion, medir_buffer, activar_motores_rotacion, reset_motores_rotacion


class Maquina_del_mal():
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.ponton = False
        self.cant_tachos = 8
        self.contenedores = {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0}
        self.buffer = None
        self.posicion_cinta = None # 1 2 3 4        
        self.posicion_cinta_cm = 8
        self.sensor = 0
        self.posicion_media = { "0": 10.5, "1": 25.5, "2": 41, "3":52.3 , "4": 6, "5": 22.5 , "6": 38.7 ,"7": 51.5} 
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

    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        if self.ponton:
            value = 1
        else:
            value = 0
        self.mqtt_client.send_metric("metricas/ponton", value)
        return self.ponton

    def ubicacion_cinta(self, sentido):  
        self.posicion_cinta_cm = self.medir_ubicacion_cinta(sentido)
        
        if 0 < self.posicion_cinta_cm < 13:
            self.posicion_cinta = 0
        elif 13 < self.posicion_cinta_cm < 30:
            self.posicion_cinta = 1
        elif  30 < self.posicion_cinta_cm < 43:
            self.posicion_cinta = 2
        elif  43 < self.posicion_cinta_cm < 51:
            self.posicion_cinta = 3
        else:
            print("Fuera de rango")
        
        self.mqtt_client.send_metric(
            "metricas/distribucion_pos", self.posicion_cinta)
        self.mqtt_client.send_metric(
            "metricas/distribucion_pos_cm", self.posicion_cinta_cm)

    def medir_llenado_tachos(self, sensor, tacho):
        if sensor == 1:
            self.contenedores[str(tacho)] = self.medir_llenado(
                sensor)  # cuando tenga los 2 sensores, hay que especificar cual usar
            topic = "metricas/tacho" + str(tacho)
            self.mqtt_client.send_metric(
                topic, self.contenedores[str(tacho)])
            print(self.contenedores[str(tacho)])
        if sensor == 2:
            self.contenedores[str(tacho)] = self.medir_llenado(sensor)
            topic = "metricas/tacho" + str(tacho)
            self.mqtt_client.send_metric(topic, self.contenedores[str(tacho)])

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

    def medir_ubicacion_cinta(self, sentido):
        
        distancia = None
        while distancia == None:
            GPIO.output(self.trigger_ubi, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(self.trigger_ubi, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(self.trigger_ubi, GPIO.LOW)

            while True:
                pulso_inicio = time.time()
                if GPIO.input(self.echo_ubi) == GPIO.HIGH:
                    break

            while True:
                pulso_fin = time.time()
                if GPIO.input(self.echo_ubi) == GPIO.LOW:
                    break

            # Tiempo medido en segundos
            duracion = pulso_fin - pulso_inicio

            # Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
            distancia = (self.sound_speed * duracion) / 2
            print(f"{distancia}")
            #return distancia
            if sentido == False:
                #print("sentido False")
                #print(f"estoy haciendo {self.posicion_cinta_cm} < {distancia} < {self.posicion_cinta_cm + 3}")
                if self.posicion_cinta_cm <  distancia < (self.posicion_cinta_cm + 3):
                    #print(distancia)
                    return distancia
                else:
                    distancia = None
            else:
                #print("sentido Truo")
                #print(f"estoy haciendo {self.posicion_cinta_cm -3} < {distancia} < {self.posicion_cinta_cm}")
                if (self.posicion_cinta_cm - 3) < distancia < self.posicion_cinta_cm:
                    print(distancia)
                    return distancia
                else:
                    distancia = None


    def medir_ubicacion_cinta_inicial(self):
        
            GPIO.output(self.trigger_ubi, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(self.trigger_ubi, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(self.trigger_ubi, GPIO.LOW)

            while True:
                pulso_inicio = time.time()
                if GPIO.input(self.echo_ubi) == GPIO.HIGH:
                    break

            while True:
                pulso_fin = time.time()
                if GPIO.input(self.echo_ubi) == GPIO.LOW:
                    break

            # Tiempo medido en segundos
            duracion = pulso_fin - pulso_inicio

            # Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
            distancia = (self.sound_speed * duracion) / 2
            print(f"inicial {distancia}")
            self.posicion_cinta_cm = distancia
    
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
                distancia_vacio = 14.5
                distancia_lleno = 2
        else:
                trigger =None
                echo = None
                print("No voy a medir nada")
        
        list_dist = []
        for x in range(10):    
                # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
                GPIO.output(trigger, GPIO.LOW)
                time.sleep(0.3)

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

                #Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
                distancia = (self.sound_speed * duracion) / 2
                
                # % llenado
                # hay que redefinir esto tambien ------------------------
                if distancia > distancia_vacio + 2 :
                    pass
                #elif distancia == 'nan':
                #    pass
                #elif type(distancia) != float:
                #    pass
                else:
                    list_dist.append(distancia)
        
        # Descartar mediciones que difieren significativamente de la mediana
        #mediana = np.median(list_dist)
        #diff = np.abs(list_dist - mediana)
        #mediana_absoluta = np.median(diff)
        #factor = 5  # Ajusta el factor según sea necesario
        #umbral = factor * mediana_absoluta
        #distancias_filtradas = [
        #    d for d in list_dist if np.abs(d - mediana) <= umbral]
        #distancias_descartadas = [
        #    d for d in list_dist if np.abs(d - mediana) > umbral]
        #topic = "metricas/distancias_descartadas"
        #self.mqtt_client.send_metric(
        #    topic, distancias_descartadas)
        #distancias_filtradas = np.mean(distancias_filtradas)
        #print(f'estas son las {distancias_filtradas=}')
        distancias_filtradas = np.mean(list_dist)
        porcentaje = (distancia_vacio - distancias_filtradas) * 100 / \
            (distancia_vacio - distancia_lleno)
        
        print(f'estas son las {distancias_filtradas=}')
        return porcentaje


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
        self.velocidades = [0.01, 0.009, 0.008, 0.007]
        self.velocidad = 0
        self.verbose = False
        self.init_delay = 0.01
        self.metricas = "metricas/motor_traslacion"
        self.mode_pin = (-1, -1, -1)
        self.motor_traslacion_nema = motor.A4988Nema(
            self.direcction, self.step, self.mode_pin, "A4988")

    def activar_motores_traslacion(self):
        while self.motores_status == 'on':
            time.sleep(0.01)
            self.mqtt_client.send_metric(self.metricas, 1)
            self.mqtt_client.send_metric(self.metricas+"_vel", self.velocidad)
            self.motor_traslacion_nema.motor_go(
                self.clockwise, self.step_type, self.steps, self.velocidades[self.velocidad], self.verbose, self.init_delay)

    def reset_motores_traslacion(self):
        self.motor_traslacion_nema.motor_stop()

    def fin(self):
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
        GPIO.cleanup()
        self.stop_event.set()
    
    def run(self):
        cont = 0
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                cont = 0
                self.activar_motores_rotacion()
            elif self.motores_status == 'off':
                if cont == 0:
                    print("envio las metricas de apagado 1 vez")
                    self.mqtt_client.send_metric(self.metricas, 0)
                    self.mqtt_client.send_metric(self.metricas + "_vel", self.velocidad)
                cont +=1
                time.sleep(0.5)
            else:
                pass         
                
                
class Camara(threading.Thread):
    def __init__(self, mqtt_client):
        super().__init__()
        self.daemon = True
        self.buffer = 0
        self.mqtt_client = mqtt_client
        self.metricas = "/metricas/buffer" 
    def run(self):
        
        self.mqtt_client.send_metric(self.metricas, 80)
        time.sleep(10)
        names = ["tapas_multicolor.jpg", "tapas_rojas.jpg"]
        for n in names:
            self.buffer = buffer_porcentaje(n)
            self.mqtt_client.send_metric(self.metricas, self.buffer)
            time.sleep(60)

if __name__ == "__main__":
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
