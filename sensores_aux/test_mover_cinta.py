import time
import threading
import _thread
from RpiMotorLib import RpiMotorLib as motor
import RPi.GPIO as GPIO 

#from sensores import medir_si_esta_ponton, medir_ubicacion_cinta, mover_cinta_traslacion, medir_buffer, activar_motores_rotacion, reset_motores_rotacion


class Maquina_del_mal():
    def __init__(self):
        self.ponton = False
        self.cant_tachos = 8
        self.contenedores = {"0":0,"1":0,"2":0,"3":0,"4":90,"5":90,"6":90,"7":90}
        self.buffer = None
        #self.motor_rotacion = False # True=On False=Off
        #self.motor_traslacion = False
        self.posicion_cinta = None # 1 2 3 4        
        self.posicion_cinta_cm = 0 # 1 2 3 4
        self.posicion_media = { "0": 7,
                                "1": 23,
                                "2": 39,
                                "3": 55} 

        self.set_maquina()
    
    
    def set_maquina(self):
        # ultrasonido ubicacion cinta
        GPIO.setmode(GPIO.BCM)
        self.trigger_ubi = 19
        self.echo_ubi = 26
        GPIO.setup(self.trigger_ubi, GPIO.OUT)
        GPIO.setup(self.echo_ubi, GPIO.IN)
        
        # ultrasonido llenado delantero 
        self.trigger_tacho_1 = 6
        self.echo_tacho_1 = 5
        GPIO.setup(self.trigger_tacho_1, GPIO.OUT)
        GPIO.setup(self.echo_tacho_1, GPIO.IN)
        
        # ultrasonido llenado trasero
        self.trigger_tacho_2 = 10
        self.echo_tacho_2 = 11
        #GPIO.setup(self.trigger_tacho_2, GPIO.OUT)
        #GPIO.setup(self.echo_tacho_2, GPIO.IN)
        self.sound_speed = 34300
        
        
        # IR
        #self.sensor_ir = 14
        #GPIO.setup(self.sensor_ir,GPIO.IN)


    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        return self.ponton
        
    def ubicacion_cinta(self): # existen cuatro ubicaciones
        self.posicion_cinta_cm = self.medir_ubicacion_cinta()
        print(f"Distancia: {self.posicion_cinta_cm} cm")
        if 0 < self.posicion_cinta_cm < 15:
            print(0)
            self.posicion_cinta = 0
        elif 15 < self.posicion_cinta_cm < 31:
            print(1)
            self.posicion_cinta = 1
        elif  31 < self.posicion_cinta_cm < 47:
            print(2)
            self.posicion_cinta = 2
        elif  47 < self.posicion_cinta_cm < 63:
            print(3)
            self.posicion_cinta = 3
        else:
            print( "Fuera de rango")

    def medir_llenado_tachos(self, sensor):
        if sensor == 1:
            self.contenedores[str(self.posicion_cinta)] = self.medir_llenado(sensor)
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
            sound_speed = 343000
            # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
            GPIO.output(self.trigger_ubi, GPIO.LOW)
            time.sleep(0.5)

            #Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajo
            GPIO.output(self.trigger_ubi, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(self.trigger_ubi, GPIO.LOW)

            # En este momento el sensor envía 8 pulsos ultrasónicos de 40kHz y coloca su pin ECHO en alto
            # Debemos detectar dicho evento para iniciar la medición del tiempo
            
            while True:
                pulso_inicio = time.time()
                if GPIO.input(self.echo_ubi) == GPIO.HIGH:
                    break

            # El pin ECHO se mantendrá en HIGH hasta recibir el eco rebotado por el obstáculo. 
            # En ese momento el sensor pondrá el pin ECHO en bajo.
            # Prodedemos a detectar dicho evento para terminar la medición del tiempo
            
            while True:
                pulso_fin = time.time()
                if GPIO.input(self.echo_ubi) == GPIO.LOW:
                    break

            # Tiempo medido en segundos
            duracion = pulso_fin - pulso_inicio

            #Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
            distancia = (sound_speed * duracion) / 20
            return distancia
    
    def medir_llenado(self, sensor):
        #if sensor == 1:
        trigger = self.trigger_tacho_1
        echo = self.echo_tacho_1
        #elif sensor == 2:
        #    trigger = self.trigger_tacho_1
        #    echo = self.echo_tacho_1
        #else:
        #    trigger =None
        #    echo = None
        #    print("No voy a medir nada")
            
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
        distancia_vacio = 17.2
        distancia_lleno = 11
        print(distancia)
        porcentaje = (distancia_vacio - distancia) * 100 / (distancia_vacio - distancia_lleno)
        print(f"{porcentaje=}")
        return porcentaje
    
        
        
class Motores_traslacion(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = None # "right" "left"
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



        self.mode_pin = (-1,-1,-1)
        self.motor_traslacion_nema = motor.A4988Nema(self.direcction, self.step, self.mode_pin, "A4988")
        
    def activar_motores_traslacion(self):
        while self.motores_status == 'on':
            time.sleep(0.01)
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
        
class Motores_rotacion(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = None # "right" "left"
        self.config()
        self.stop_event = threading.Event()
        

    def config(self):
        self.dir = 26 #naranja
        self.step = 19 #azul
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
            GPIO.output(self.dir,1)
            
            while self.motores_status == "on":
                time.sleep(0.01)
                # Run for 200 steps. This will change based on how you set you controller
                for x in range(200):

                    # Set one coil winding to high
                    GPIO.output(self.step,GPIO.HIGH)
                    # Allow it to get there.
                    time.sleep(self.velocidad) # Dictates how fast stepper motor will run
                    # Set coil winding to low
                    GPIO.output(self.step,GPIO.LOW)
                    time.sleep(self.velocidad) # Dictates how fast stepper motor will run
                    #finish_time = time.time()
    def fin(self):
        self.stop_event.set()
    
    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                self.activar_motores_rotacion()
            elif self.motores_status == 'off':
                #print("se deberia apagar")
                #self.reset_motores_traslacion()
                time.sleep(0.1)
            else:
                pass


def elegir_tacho_a_llenar(contenedores: dict) -> int or False :
    aux = []
    for contenedor in range(len(contenedores)):
        aux.append(contenedores[str(contenedor)])

    posible_opcion =aux.index(min(aux))
    if posible_opcion <= 4:
        clockwise = True
    else:
        clockwise = False

    if contenedores[str(posible_opcion)] > 95:
        posible_opcion = False

    return posible_opcion, clockwise

def mover_cinta(maquina, traslacion, pos):       
    if (maquina.posicion_cinta - pos) > 0 :
        traslacion.clockwise = False
        traslacion.motores_status = "on"
        print(f"{maquina.posicion_media[str(pos)]=}")
        print(f"{maquina.posicion_cinta_cm}")
        while not ( (maquina.posicion_media[str(pos)] - 1) < maquina.posicion_cinta_cm < (maquina.posicion_media[str(pos)] + 1)) :
            #print(" no salgo del while")
            maquina.ubicacion_cinta()
            time.sleep(0.2)
        traslacion.motores_status = "off"
    elif (maquina.posicion_cinta - pos) < 0: 
        traslacion.clockwise = True
        traslacion.motores_status = "on"
        while not( maquina.posicion_media[str(pos)] - 1 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)] + 1) :
            maquina.ubicacion_cinta()
            time.sleep(0.2)
        traslacion.motores_status = "off"
    else:
        print("ya estoy aca segui")
    print("llegue al que elegi, ahora lleno")


if __name__ == "__main__":
        
    traslacion = Motores_traslacion()
    #maquina = Maquina_del_mal()
    #rotacion = Motores_rotacion()
    time.sleep(1)
    traslacion.start()
    #rotacion.start()
    time.sleep(3)
    print("Arranca todo")
    #maquina.ubicacion_cinta()
    #for pos in range(4):
    #    print(f"{pos=} y {maquina.posicion_cinta}")
    #    time.sleep(0.8)
    #    mover_cinta(maquina, traslacion, pos)
    #    print("mido los tachos")
    #    maquina.medir_llenado_tachos(1)
    #    #maquina.medir_llenado_tachos(2)
    #print("Medi todos, ahora lleno")
    #x,y = elegir_tacho_a_llenar(maquina.contenedores)
    
    
    #print(f"Elijo {x=} {y=}")
    #print(f"{maquina.contenedores=}")
    
    #mover_cinta(maquina, traslacion, x)
    
    #while maquina.contenedores[str(maquina.posicion_cinta)] < 60:
    end = time.time()
    start = time.time()
    
    while end - start < 10:
        traslacion.motores_status = "on"
        #maquina.medir_llenado_tachos(1)
        time.sleep(0.5)
        end = time.time()
    rotacion.motores_status = "off"

    #traslacion.fin()
    rotacion.fin()
    
