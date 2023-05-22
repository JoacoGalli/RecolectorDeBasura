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
        self.contenedores = {"0": 0, "1": 0, "2": 0,
                             "3": 0, "4": 90, "5": 90, "6": 90, "7": 90}
        self.buffer = None
        self.posicion_cinta = None  # 1 2 3 4
        self.posicion_cinta_cm = 0
        self.posicion_media = {"0": 7, "1": 23, "2": 39, "3": 55}
        self.set_maquina()

    def set_maquina(self):
        # ultrasonido ubicacion cinta
        GPIO.setmode(GPIO.BCM)
        self.trigger_ubi = 14
        self.echo_ubi = 15
        GPIO.setup(self.trigger_ubi, GPIO.OUT)
        GPIO.setup(self.echo_ubi, GPIO.IN)

        # ultrasonido llenado delantero
        self.trigger_tacho_1 = 16
        self.echo_tacho_1 = 18
        GPIO.setup(self.trigger_tacho_1, GPIO.OUT)
        GPIO.setup(self.echo_tacho_1, GPIO.IN)

        # ultrasonido llenado trasero
        # self.trigger_tacho_2 = 7
        # self.echo_tacho_2 = 24
        # GPIO.setup(self.trigger_tacho_2, GPIO.OUT)
        # GPIO.setup(self.echo_tacho_2, GPIO.IN)
        self.sound_speed = 34300

        # IR
        self.sensor_ir = 21
        GPIO.setup(self.sensor_ir, GPIO.IN)

    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        self.mqtt_client.send_metric("metricas/ponton", self.ponton)
        return self.ponton

    def ubicacion_cinta(self):  # existen cuatro ubicaciones
        # esto lo deberiamos rechequear
        self.posicion_cinta_cm = self.medir_ubicacion_cinta()
        # print(f"Distancia: {self.posicion_cinta_cm} cm")
        if 0 < self.posicion_cinta_cm < 15:
            # print(0)
            self.posicion_cinta = 0
        elif 15 < self.posicion_cinta_cm < 31:
            # print(1)
            self.posicion_cinta = 1
        elif 31 < self.posicion_cinta_cm < 47:
            # print(2)
            self.posicion_cinta = 2
        elif 47 < self.posicion_cinta_cm < 63:
            # print(3)
            self.posicion_cinta = 3
        else:
            print("Fuera de rango")
        self.mqtt_client.send_metric(
            "metricas/distribucion_pos", self.posicion_cinta)
        self.mqtt_client.send_metric(
            "metricas/distribucion_pos_cm", self.posicion_cinta_cm)

    def medir_llenado_tachos(self, sensor):
        if sensor == 1:
            self.contenedores[str(self.posicion_cinta)] = self.medir_llenado(
                sensor)  # cuando tenga los 2 sensores, hay que especificar cual usar
            topic = "metricas/tacho" + str(self.posicion_cinta)
            self.mqtt_client.send_metric(
                topic, self.contenedores[str(self.posicion_cinta)])
        if sensor == 2:
            pass
            # self.contenedores[str(self.posicion_cinta + 4)] = self.medir_llenado(sensor,2)
            # topic = "metricas/tacho" + str(self.posicion_cinta + 4)
            # self.mqtt_client.send_metric(topic, self.contenedores[str(self.posicion_cinta)])

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

    def medir_ubicacion_cinta(self,):
        # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
        GPIO.output(self.trigger_ubi, GPIO.LOW)
        time.sleep(0.5)

        # Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajoz
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
        return distancia

    def medir_llenado(self, sensor):
        trigger = None
        echo = None

        if sensor == 1:
            trigger = self.trigger_tacho_1
            echo = self.echo_tacho_1
        elif sensor == 2:
            trigger = self.trigger_tacho_1
            echo = self.echo_tacho_1
        else:
            print("No voy a medir nada")

        list_dist = []
        for x in range(10):
            # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
            GPIO.output(trigger, GPIO.LOW)
            time.sleep(0.5)

            # Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajo
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
            distancia = (self.sound_speed * duracion) / 2

            # % llenado
            # hay que redefinir esto tambien ------------------------
            list_dist.append(distancia)

        # Descartar mediciones que difieren significativamente de la mediana
        mediana = np.median(list_dist)
        diff = np.abs(list_dist - mediana)
        mediana_absoluta = np.median(diff)
        factor = 5  # Ajusta el factor según sea necesario
        umbral = factor * mediana_absoluta
        distancias_filtradas = [
            d for d in list_dist if np.abs(d - mediana) <= umbral]
        distancias_descartadas = [
            d for d in list_dist if np.abs(d - mediana) > umbral]
        topic = "metricas/distancias_descartadas"
        self.mqtt_client.send_metric(
            topic, distancias_descartadas)

        # print(f"{list_dist=}")
        # dist_mean = mean(list_dist)
        distancia_vacio = 18.2
        distancia_lleno = 11
        print(f"{distancias_filtradas=}")
        porcentaje = (distancia_vacio - distancias_filtradas) * 100 / \
            (distancia_vacio - distancia_lleno)

        return porcentaje


class Motores_traslacion(threading.Thread):

    def __init__(self, mqtt):
        threading.Thread.__init__(self)
        self.mqtt_client = mqtt
        self.deamon = True
        self.motores_status = 'off'  # on, off, reset
        self.sentido = None  # "right" "left"
        self.config()
        self.stop_event = threading.Event()

    def config(self):
        # motor
        self.direcction = 17
        self.step = 27
        self.cw = 1
        self.ccw = 0
        self.clockwise = True
        self.step_type = "Full"
        self.steps = 100
        self.step_delay = 0.005
        self.verbose = False
        self.init_delay = 0.01

        self.mode_pin = (-1, -1, -1)
        self.motor_traslacion_nema = motor.A4988Nema(
            self.direcction, self.step, self.mode_pin, "A4988")

    def activar_motores_traslacion(self):
        while self.motores_status == 'on':
            time.sleep(0.01)
            self.mqtt_client.send_metric("metricas/motor_traslacion", 1)
            self.motor_traslacion_nema.motor_go(
                self.clockwise, self.step_type, self.steps, self.step_delay, self.verbose, self.init_delay)

    def reset_motores_traslacion(self):
        self.motor_traslacion_nema.motor_stop()
        self.mqtt_client.send_metric("metricas/motor_traslacion", 0)

    def fin(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                self.activar_motores_traslacion()
            elif self.motores_status == 'off':
                self.reset_motores_traslacion()
                time.sleep(0.1)
            else:
                pass


class Motores_rotacion(threading.Thread):
    def __init__(self, mqtt):
        threading.Thread.__init__(self)
        self.mqtt_client = mqtt
        self.deamon = True
        self.motores_status = 'off'  # on, off, reset
        self.sentido = None  # "right" "left"
        self.config()
        self.stop_event = threading.Event()

    def config(self):
        # ver si los definimos a los 2 iguales
        self.dir = 26
        self.step = 19
        self.velocidad = .01

        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)

        # Set the first direction you want it to spin
        GPIO.output(self.dir, 1)

    def activar_motores_rotacion(self):

        print("rotando")
        GPIO.output(self.dir, 1)
        self.mqtt_client.send_metric("metricas/motor_rotacion_cap", 1)
        self.mqtt_client.send_metric(
            "metricas/motor_rotacion_cap_vel", self.velocidad)
        while self.motores_status == "on":
            time.sleep(0.01)
            # Run for 200 steps. This will change based on how you set you controller
            for x in range(200):

                # Set one coil winding to high
                GPIO.output(self.step, GPIO.HIGH)
                # Allow it to get there.
                # Dictates how fast stepper motor will run
                time.sleep(self.velocidad)
                # Set coil winding to low
                GPIO.output(self.step, GPIO.LOW)
                # Dictates how fast stepper motor will run
                time.sleep(self.velocidad)
                # finish_time = time.time()

    def fin(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                self.activar_motores_rotacion()
            elif self.motores_status == 'off':
                self.mqtt_client.send_metric("metricas/motor_rotacion_cap", 0)
                self.mqtt_client.send_metric(
                    "metricas/motor_rotacion_cap_vel", 0)
                # print("se deberia apagar")
                # self.reset_motores_traslacion()
                time.sleep(0.1)
            else:
                pass


class Camara(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.buffer = None

    def run(self):
        names = ["tapas_multicolor.jpg", "tapas_rojas.jpg"]
        for n in names:
            self.buffer = buffer_porcentaje(n)
            time.sleep(60)  # 60 segundos?
