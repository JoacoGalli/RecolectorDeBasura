import time
import threading
from RpiMotorLib import RpiMotorLib as motor
import RPi.GPIO as GPIO 

#from sensores import medir_si_esta_ponton, medir_ubicacion_cinta, mover_cinta_traslacion, medir_buffer, activar_motores_rotacion, reset_motores_rotacion



class Maquina_del_mal(threading.Thread):
    def __init__(self):
        super().__init__()
        self.ponton = False
        self.cant_tachos = 8
        self.contenedores = {"1":0} #{"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0}
        self.buffer = None
        self.motor_rotacion = False # True=On False=Off
        self.motor_traslacion = False
        self.posicion_cinta = None # 1 2 3 4 
        self.set_maquina()

    
    
    def set_maquina(self):
        # ultrasonido
        self.trigger = 6
        self.echo = 5
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        self.sound_speed = 34300
        
        # IR
        self.sensor_ir = 14
        GPIO.setup(self.sensor_ir,GPIO.IN)
        
        #motor
        self.direcction = 21
        self.step = 20
        self.clockwise = False
        self.step_type = "Full"
        self.steps = 800
        self.step_delay = 0.005
        self.verbose = False
        self.init_delay = 0.01


        self.mode_pin = (-1,-1,-1)
        self.motor_traslacion_nema = motor.A4988Nema(self.direcction, self.step, self.mode_pin, "A4988")
        

    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        return self.ponton
    
    def ubicacion_cinta(self): # existen cuatro ubicaciones
        self.posicion_cinta = self.medir_ubicacion_cinta()
        return self.posicion_cinta

    def trasladar_cinta(self, nueva_posicion=5):
        self.motor_traslacion = True
        if self.mover_cinta_traslacion(nueva_posicion):
            self.mover_motor(clockwise)

    def medir_llenado_tachos(self):
        self.contenedores["1"] = medir_llenado()
        #self.contenedores[str(self.posicion_cinta)], self.contenedores[str(self.posicion_cinta + 4)] = medir_llenado()
        pass


    def medir_ubicacion_cinta(self):
        # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
        GPIO.output(self.trigger, GPIO.LOW)
        time.sleep(0.5)

        #Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajo
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)

        # En este momento el sensor envía 8 pulsos ultrasónicos de 40kHz y coloca su pin ECHO en alto
        # Debemos detectar dicho evento para iniciar la medición del tiempo
        
        while True:
            pulso_inicio = time.time()
            if GPIO.input(self.echo) == GPIO.HIGH:
                break

        # El pin ECHO se mantendrá en HIGH hasta recibir el eco rebotado por el obstáculo. 
        # En ese momento el sensor pondrá el pin ECHO en bajo.
	# Prodedemos a detectar dicho evento para terminar la medición del tiempo
        
        while True:
            pulso_fin = time.time()
            if GPIO.input(self.echo) == GPIO.LOW:
                break

        # Tiempo medido en segundos
        duracion = pulso_fin - pulso_inicio

        #Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
        distancia = (self.sound_speed * duracion) / 2
        print(distancia)
        return distancia 
        # Imprimimos resultado
        
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

    def mover_cinta_traslacion(self, nueva_posicion):
        print("entre a la funcion")
        self.medir_ubicacion_cinta()
        while self.posicion_cinta < nueva_posicion:
            print("arranca")
            start_time = time.time()
            finish_time = time.time()
            while finish_time - start_time < 10:
                time.sleep(0.01)
                self.motor_traslacion_nema.motor_go(self.clockwise, self.step_type, self.steps, self.step_delay, self.verbose, self.init_delay)
                finish_time = time.time()
            self.medir_ubicacion_cinta()
        if self.posiciones_cinta > nueva_posicion:
            print("estoy aca?")
            self.clocwise = False
            while self.posiciones_cinta > (nueva_posicion - 0.5):
                for i in range(10000):
                    time.sleep(0.01)
                    self.motor_traslacion_nema.motor_go(self.clockwise, self.step_type, self.steps, self.step_delay, self.verbose, self.init_delay)
                self.medir_ubicacion_cinta()                
        print("la corri a donde me dijiste")

            
class Motores_traslacion(threading.Thread): # posdemos usar 1 solo thread??
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = None # "right" "left"
        self.config()
        self.stop_event = threading.Event()
        
    def config(self):
        # motor
        self.direcction = 21
        self.step = 20
        self.cw = 1
        self.ccw = 0
        self.clockwise = False
        self.step_type = "Full"
        self.steps = 8000
        self.step_delay = 0.00005
        self.verbose = False
        self.init_delay = 0.01


        self.mode_pin = (-1,-1,-1)
        self.motor_traslacion_nema = motor.A4988Nema(self.direcction, self.step, self.mode_pin, "A4988")
        
    def activar_motores_traslacion(self):
#        start_time = time.time()
#        finish_time = time.time()
#        while finish_time - start_time < 2:
        print('{self.clowise=}')
        self.motor_traslacion_nema.motor_go(self.clockwise, self.step_type, self.steps, self.step_delay, self.verbose, self.init_delay)
        #finish_time = time.time()
    
    def reset_motores_traslacion(self):
        self.motor_traslacion_nema.motor_stop()
        print("lo apague")
    
    def fin(self):
        self.stop_event.set()
        
    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                print("estoy moviendo")
                self.activar_motores_traslacion()
            else:# self.motores_status == 'off':
                print("se deberia apagar")
                self.reset_motores_traslacion()


class Motores_rotacion(threading.Thread): # posdemos usar 1 solo thread??
    def __init__(self):
        super().__init__()
        self.status = True
        self.daemon = True
        self.motores_status = 'off' # on, off, reset
        #self.sentido = None # "right" "left"
        self.dir = 23 #naranja
# Step pin from controller
        self.step = 24 #azul
# 0/1 used to signify clockwise or counterclockwise.
        self.cw = 1
        self.ccw = 0
        self.config()
        self.velocidad = .001

    def config(self):
        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)

        # Set the first direction you want it to spin
        GPIO.output(self.dir, 0)

        
    def activar_motores_rotacion(self):
 #       start_time = time.time()
 #       finish_time = time.time()
 #       while finish_time - start_time < 10:
            print("rotando")
            GPIO.output(self.dir,0)
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
    
    def reset_motores_rotacion(self):
        pass
    
    def run(self):
        while(self.status):
            if self.motores_status == 'on':
                print("estamos activo")
                self.activar_motores_rotacion()
            else:#if self.motores_status == 'reset':
                self.reset_motores_rotacion()
                self.motores_status = 'off'



if __name__ == "__main__":
    # se setea con GPIO.BCM option means these are the numbers after "GPIO"
    #traslacion = Motores_traslacion()
    #time.sleep(1)
    #traslacion.start()
    #start_time = time.time()
    #finish_time = time.time()
    #time.sleep(2)
    #while finish_time - start_time < 5:
    #    traslacion.motores_status = "on"
    #    finish_time = time.time()
    #traslacion.motores_status = "off"
    #time.sleep(5)
    #traslacion.fin()
#while finish_time - start_time < 5:
    #    traslacion.clocwise = False
    #    traslacion.motores_status = "on"
    #    finish_time = time.time()
    #traslacion.motores_status = "off"
    #print("frene")
    #time.sleep(5)
    
    # se setea con GPIO.BCM option means these are the numbers after "GPIO"
    #rotacion = Motores_rotacion()
    #maquina = Maquina_del_mal()
    #rotacion.start()
    #start_time = time.time()
    #finish_time = time.time()
    #while finish_time - start_time < 10:
    #rotacion.motores_status = "on"
    #finish_time = time.time()
        #maquina.ubicacion_cinta()
    #rotacion.motores_status = "off"

    #rotacion.velocidad = 0.01
    #start_time = time.time()
    #finish_time = time.time()
    #while finish_time - start_time < 10:
    #    rotacion.motores_status = "on"
    #    finish_time = time.time()
    #rotacion.motores_status = "off"


    #traslacion = Motores_traslacion()
    #traslacion.start()
    #rotacion = Motores_rotacion()
    #rotacion.start()
    GPIO.setmode(GPIO.BCM)    
    maquina = Maquina_del_mal()
    #maquina.start()
    print("Mido la cinta")
    maquina.ubicacion_cinta()
    #maquina.mover_cinta_traslacion(30)
    #print(f" la que comparo es {maquina.posicion_cinta=}")
    #while maquina.posicion_cinta < 17.80:
    #    traslacion.motores_status = "on"
    #    maquina.ubicacion_cinta()
    #    print(f" la que comparo es {maquina.posicion_cinta=}") 
    #traslacion.motores_status = "off"
    #start_time = time.time()
    #finish_time = time.time()
    #while finish_time - start_time < 7.80:
    #    rotacion.motores_status = "on"
    #    finish_time = time.time()
    #print("Termino")
    #rotacion.status = False
    #maquina.stop()
