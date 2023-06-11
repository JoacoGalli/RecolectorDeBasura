import time
import threading
from RpiMotorLib import RpiMotorLib as motor
import RPi.GPIO as GPIO 
from statistics import mean
from new_buffer import buffer_porcentaje

#from sensores import medir_si_esta_ponton, medir_ubicacion_cinta, mover_cinta_traslacion, medir_buffer, activar_motores_rotacion, reset_motores_rotacion

class Maquina_del_mal():
    def __init__(self):
        self.ponton = False
        self.cant_tachos = 8
        self.contenedores = {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0}
        self.buffer = None
        self.posicion_cinta = None # 1 2 3 4        
        self.posicion_cinta_cm = 0
        self.sensor = 0
        self.posicion_media = { "0": 9, "1": 22, "2": 36, "3": 48} 
        self.set_maquina()
    
    def set_maquina(self):
        # ultrasonido ubicacion cinta
        GPIO.setmode(GPIO.BCM)
        self.trigger_ubi = 7
        self.echo_ubi = 24
        GPIO.setup(self.trigger_ubi, GPIO.OUT)
        GPIO.setup(self.echo_ubi, GPIO.IN)
        
        # ultrasonido llenado delantero 
        self.trigger_tacho_1 = 14        
        self.echo_tacho_1 = 15
        GPIO.setup(self.trigger_tacho_1, GPIO.OUT)
        GPIO.setup(self.echo_tacho_1, GPIO.IN)

        # ultrasonido llenado trasero
        self.trigger_tacho_2 = 16
        self.echo_tacho_2 = 18
        GPIO.setup(self.trigger_tacho_2, GPIO.OUT)
        GPIO.setup(self.echo_tacho_2, GPIO.IN)
        self.sound_speed = 34300
        
        # IR
        self.sensor_ir = 21
        GPIO.setup(self.sensor_ir,GPIO.IN)
        
        
    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        return self.ponton
        
    def ubicacion_cinta(self): # existen cuatro ubicaciones
        # esto lo deberiamos rechequear
        self.posicion_cinta_cm = self.medir_ubicacion_cinta()
        #print(f"Distancia: {self.posicion_cinta_cm} cm")
        if 0 < self.posicion_cinta_cm < 13:
            #print(0)
            self.posicion_cinta = 0
        elif 13 < self.posicion_cinta_cm < 30:
            #print(1)
            self.posicion_cinta = 1
        elif  30 < self.posicion_cinta_cm < 43:
            #print(2)
            self.posicion_cinta = 2
        elif  43 < self.posicion_cinta_cm < 49:
            #print(3)
            self.posicion_cinta = 3
        else:
            print( "Fuera de rango")

    def medir_llenado_tachos(self, sensor):
        if sensor == 1:
            self.contenedores[str(self.posicion_cinta)] = self.medir_llenado(sensor) # cuando tenga los 2 sensores, hay que especificar cual usar
        if sensor == 2:
            self.contenedores[str(self.posicion_cinta + 4)] = self.medir_llenado(sensor)

    def medir_si_esta_ponton(self):
        print("Estamos listos para arrancar a medir")
        ti = time.time()
        tf = time.time()
        while(tf - ti < 1):
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

            #Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajoz
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

            #Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
            distancia = (self.sound_speed * duracion) / 2
            return distancia
    
    def medir_llenado(self, sensor):
        #trigger = self.trigger_tacho_1
        #echo = self.echo_tacho_1
        if sensor == 2:
                trigger = self.trigger_tacho_2
                echo = self.echo_tacho_2
                distancia_vacio = 13
                distancia_lleno = 2
        elif sensor == 1:
                trigger = self.trigger_tacho_1
                echo = self.echo_tacho_1
                distancia_vacio = 11
                distancia_lleno = 1.5
        else:
                trigger =None
                echo = None
                print("No voy a medir nada")
        
        list_dist = []
        for x in range(10):    
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

                #Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
                distancia = (self.sound_speed * duracion) / 2
                
                # % llenado
                # hay que redefinir esto tambien ------------------------
                print(f"{distancia=}")
                print(f"{sensor}")
                if distancia > distancia_vacio:
                        print("lo descarto")
                        pass
                else:
                        print("lo apendeo")
                        list_dist.append(distancia)
        #print(f"{list_dist=}")
        
        dist_mean = mean(list_dist)
        #print(f"{dist_mean=}")
        porcentaje = (distancia_vacio - dist_mean) * 100 / (distancia_vacio - distancia_lleno)
                
        return porcentaje
    
        
        
class Motores_traslacion(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
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
        self.step_delay = 0.005
        self.verbose = False
        self.init_delay = 0.01



        self.mode_pin = (-1,-1,-1)
        self.motor_traslacion_nema = motor.A4988Nema(self.direcction, self.step, self.mode_pin, "A4988")
        
    def activar_motores_traslacion(self):
        while self.motores_status == 'on':
            time.sleep(0.01)
            #print("estoy aca")
            self.motor_traslacion_nema.motor_go(self.clockwise, self.step_type, self.steps, self.step_delay, self.verbose, self.init_delay)


    def reset_motores_traslacion(self):
        self.motor_traslacion_nema.motor_stop()
        

    def fin(self):
        self.stop_event.set()
        
    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                self.activar_motores_traslacion()
            elif self.motores_status == 'off':
                #print("se deberia apagar")
                self.reset_motores_traslacion()
                time.sleep(0.1)
            else:
                pass
        
class Motores_rotacion_dist(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = 0 #en 1 por que solo nos interesa que gire en ese sentido #None # "right" "left"
        self.config()
        self.stop_event = threading.Event()
        self.velocidades = [0.01, 0.009, 0.008, 0.007]
        self.velocidad = 0

    def config(self):
        # ver si los definimos a los 2 iguales
        self.dir = 5 
        self.step = 6 
        self.velocidad = 0
        
        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)

        # Set the first direction you want it to spin
        #GPIO.output(self.dir, self.sentido)

    def activar_motores_rotacion(self):

            print("rotando cap")
            GPIO.output(self.dir,self.sentido)
            print(f"estoy girando para {self.sentido=}")
            
            while self.motores_status == 'on':
                #time.sleep(self.velocidad)
                # Run for 200 steps. This will change based on how you set you controller
            #for x in range(10):
                    # Set one coil winding to high
                GPIO.output(self.step,GPIO.HIGH)
                    # Allow it to get there.
                time.sleep(self.velocidades[self.velocidad]) # Dictates how fast stepper motor will run
                    # Set coil winding to low
                GPIO.output(self.step,GPIO.LOW)
                time.sleep(self.velocidades[self.velocidad]) # Dictates how fast stepper motor will run
                    #finish_time = time.time()
                #time.sleep(0.5)
                #print(self.motores_status)
    
    def fin(self):
        print("lo mato")
        GPIO.cleanup()
        self.stop_event.set()
    
    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                #print("Dale prendee")
                self.activar_motores_rotacion()
            elif self.motores_status == 'off':
                #print("se deberia apagar")
                #self.reset_motores_traslacion()
                time.sleep(0.1)
            else:
                pass         
                
                
class Motores_rotacion_cap(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = 1 #en 1 por que solo nos interesa que gire en ese sentido #None # "right" "left"
        self.config()
        self.stop_event = threading.Event()
        self.velocidades = [0.01, 0.009, 0.008, 0.007]
        self.velocidad = 0

    def config(self):
        # ver si los definimos a los 2 iguales
        self.dir = 26
        self.step = 19
        self.velocidad = 0

        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)

        # Set the first direction you want it to spin
        #GPIO.output(self.dir, self.sentido)

    def activar_motores_rotacion(self):

            print("rotando cap")
            GPIO.output(self.dir,self.sentido)
            print(f"estoy girando para {self.sentido=}")
            
            while self.motores_status == 'on':
                #time.sleep(self.velocidad)
                # Run for 200 steps. This will change based on how you set you controller
            #for x in range(10):
                    # Set one coil winding to high
                GPIO.output(self.step,GPIO.HIGH)
                    # Allow it to get there.
                time.sleep(self.velocidades[self.velocidad]) # Dictates how fast stepper motor will run
                    # Set coil winding to low
                GPIO.output(self.step,GPIO.LOW)
                time.sleep(self.velocidades[self.velocidad]) # Dictates how fast stepper motor will run
                    #finish_time = time.time()
                #time.sleep(0.5)
                #print(self.motores_status)
    
    def fin(self):
        #print("lo mato")
        GPIO.cleanup()
        self.stop_event.set()
    
    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                #print("Dale prendee")
                self.activar_motores_rotacion()
            elif self.motores_status == 'off':
                #print("se deberia apagar")
                #self.reset_motores_traslacion()
                time.sleep(0.1)
            else:
                pass         
                


class Camara(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.buffer = 0
    
    def run(self):
        names = ["tapas_multicolor.jpg", "tapas_rojas.jpg"]
        for n in names:
            self.buffer = buffer_porcentaje(n)
            time.sleep(60) #60 segundos?

if __name__== "__main__":
        print("arranca este")
        #GPIO.cleanup()
        
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setmode(GPIO.BCM)
        motor = Motores_rotacion_dist()
        motor2 = Motores_rotacion_cap()
        motor.start()
        motor2.start()
        time.sleep(2)
        motor.motores_status = "on"
        motor2.motores_status = "on"
        #motor2.sentido = 0
        print("velocidad 0")
        time.sleep(5)
        print("terminaron los 10 segundos")
        motor.motores_status = 'off'
        motor2.motores_status = 'off'
        time.sleep(1)
        #motor.sentido = 1
        motor2.velocidad = 1
        motor.velocidad = 1
        print("cambie de sentido")
        time.sleep(2)
        motor.motores_status = "on"
        motor2.motores_status = "on"
        time.sleep(5)
        motor.motores_status = 'off'
        motor2.motores_status = 'off'
        time.sleep(1)
        #motor.sentido = 1
        motor2.velocidad = 2
        motor.velocidad = 2
        print("cambie de sentido")
        time.sleep(2)
        
        motor.motores_status = "on"
        motor2.motores_status = "on"
        time.sleep(5)
        motor.motores_status = 'off'
        motor2.motores_status = 'off'
        time.sleep(1)
        #motor.sentido = 1
        motor2.velocidad = 3
        motor.velocidad = 3
        print("cambie de sentido")
        time.sleep(2)
        motor.motores_status = 'off'
        motor2.motores_status = 'off'
        #motor2.velocidad = 0.009
        #print("velocidad 1")
        #time.sleep(10)
        #motor2.velocidad = 0.008
        #motor.motores_status = "off"
        #motor2.motores_status = "off"*
        #motor.sentido = 0
        #time.sleep(0.2)
        #print("velocidad 2")
        #time.sleep(10)
        #motor2.velocidad = 0.007
        #print("velocidad 3")
        #time.sleep(10)
        GPIO.cleanup()

if __name__ == "__main__2":
    #cam = Camara()
    #cam.start()
    #ti = time.time()
    #tf = time.time()
    #total = 0
    #while cam.buffer == 0:
    #    tf = time.time()
    #    total = tf - ti
    #    time.sleep(0.2)
    #print(total)
    maquina = Maquina_del_mal()
    while(True):
        maquina.esta_ponton()
        print(f'{maquina.ponton=}')


if __name__== "__main__2":
        #motor2 = Motores_traslacion()
        motor2 = Motores_rotacion_cap()
        #motor2 = Motores_rotacion_dist()
        motor2.start()
        #motor.start()
        time.sleep(1)
        #motor2.velocidad = 2
        motor2.motores_status = "on"
        print("rotando")
        time.sleep(5)
        motor2.motores_status= 'off'
        motor2.clockwise=True
        time.sleep(2)
        motor2.motores_status = 'on'
        time.sleep(10)
        GPIO.cleanup()

