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
        self.contenedores = {"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0}
        self.buffer = None
        self.motor_rotacion = False # True=On False=Off
        self.motor_traslacion = False
        self.posicion_cinta = None # 1 2 3 4 
        self.set_maquina()

    
    
    def set_maquina(self):
        # motor
        self.direcction = 21
        self.step = 20
        self.mode_pin = (-1,-1,-1)
        self.motor_traslacion_nema = motor.A4988Nema(self.direcction, self.step, self.mode_pin, "A4988")

        # ultrasonido
        self.trigger = 23
        self.echo = 24
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

        # IR
        self.sensor_ir = 14
        GPIO.setup(self.sensor_ir,GPIO.IN)


    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        return self.ponton
    
    def ubicacion_cinta(self): # existen cuatro ubicaciones
        self.posicion_cinta = self.medir_ubicacion_cinta()
        return self.posicion_cinta

    def trasladar_cinta(self, nueva_posicion=5):
        self.motor_traslacion = True
        if self.mover_cinta_traslacion(nueva_posicion):
            self.motor_traslacion = False

    def medir_llenado_tachos(self):
        #self.contenedores[str(self.posicion_cinta)], self.contenedores[str(self.posicion_cinta + 4)] = medir_llenado()
        pass


    def medir_ubicacion_cinta(self):
        # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
        #pulse_end_time = 0
        #pulse_start_tiem = 0
        GPIO.output(self.trigger, GPIO.LOW)
        #print("Waiting for sensor to settle")
        time.sleep(2)
        #print("Calculating distance")
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)
        while GPIO.input(self.echo)==0:
            pulse_start_time = time.time()
        while GPIO.input(self.echo)==1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        print("Distancia:",distance,"cm")
        return distance

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
        start_time = time.time()
        finish_time = time.time()
        clockwise = False
        step_type = "Full"
        steps = 100
        step_delay = 0.01
        verbose = False
        init_delay = 0.01

        #len_pos = nueva_posicion - self.posicion_cinta
        # clockwise puede cambiar 
        # dependiendo la posicion y el sentido elijo el tiempo con un dicionario

        while finish_time - start_time < 12:
            #self.motor_traslacion_nema.motor_go(clockwise, step_type, steps, step_delay, verbose, init_delay)
            finish_time = time.time()
            
class Motores_traslacion(threading.Thread): # posdemos usar 1 solo thread??
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = None # "right" "left"
        self.config()
        self.status = True
    def config(self):
        # motor
        self.direcction = 6
        self.step = 5
        self.cw = 1
        self.ccw = 0
        self.clockwise = False
        self.step_type = "Full"
        self.steps = 100
        self.step_delay = 0.01
        self.verbose = False
        self.init_delay = 0.01


        self.mode_pin = (-1,-1,-1)
        self.motor_traslacion_nema = motor.A4988Nema(self.direcction, self.step, self.mode_pin, "A4988")
        
    def activar_motores_traslacion(self):
        start_time = time.time()
        finish_time = time.time()
        while finish_time - start_time < 2:
            self.motor_traslacion_nema.motor_go(self.clockwise, self.step_type, self.steps, self.step_delay, self.verbose, self.init_delay)
            finish_time = time.time()
    
    def reset_motores_traslacion(self):
        self.motor_traslacion_nema.motor_stop()
        
    def run(self):
        while(self.status):
            if self.motores_status == 'on':
                print("estamos activo")
                self.activar_motores_traslacion()
            else:#if self.motores_status == 'reset':
                self.reset_motores_traslacion()
                self.motores_status = 'off'

class Motores_rotacion(threading.Thread): # posdemos usar 1 solo thread??
    def __init__(self):
        super().__init__()
        self.status = True
        self.daemon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = None # "right" "left"
        self.dir = 21 #naranja
# Step pin from controller
        self.step = 20
# 0/1 used to signify clockwise or counterclockwise.
        self.cw = 1
        self.ccw = 0
        self.config()

    def config(self):
        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)

        # Set the first direction you want it to spin
        GPIO.output(self.dir, self.cw)

        
    def activar_motores_rotacion(self):
        start_time = time.time()
        finish_time = time.time()
        while finish_time - start_time < 10:
            print("rotando")
            GPIO.output(self.dir,self.ccw)
# Run for 200 steps. This will change based on how you set you controller
            for x in range(200):

                # Set one coil winding to high
                GPIO.output(self.step,GPIO.HIGH)
                # Allow it to get there.
                time.sleep(.009) # Dictates how fast stepper motor will run
                # Set coil winding to low
                GPIO.output(self.step,GPIO.LOW)
                time.sleep(.009) # Dictates how fast stepper motor will run
                finish_time = time.time()
    
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
    traslacion = Motores_traslacion()
    traslacion.start()
    
    rotacion = Motores_rotacion()
    rotacion.start()
    
    maquina = Maquina_del_mal()
    #maquina.start()
    #time.sleep(5)
    #traslacion.config()
    #ponton = maquina.esta_ponton()
    print("Mido la cinta")
    maquina.ubicacion_cinta()
    #maquina.trasladar_cinta()
    while maquina.posicion_cinta < 37.5:
        print("Tengo que seguir midiendo")
        traslacion.motores_status = "on"
        maquina.ubicacion_cinta()
    traslacion.motores_status = "off"
    start_time = time.time()
    finish_time = time.time()
    while finish_time - start_time < 15:
        rotacion.motores_status = "on"
        finish_time = time.time()
    print("Termino")
    traslacion.status = False
    rotacion.status = False
    traslacion.join()
    #maquina.stop()
    rotacion.join()
