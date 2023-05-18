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
        self.contenedores = {"1":0} #{"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0}
        self.buffer = None
        #self.motor_rotacion = False # True=On False=Off
        #self.motor_traslacion = False
        self.posicion_cinta = 0 # 1 2 3 4        
        self.posicion_cinta_cm = 0 # 1 2 3 4 

         
        self.set_maquina()
    
    
    def set_maquina(self):
        # ultrasonido
        GPIO.setmode(GPIO.BCM)
        self.trigger = 19
        self.echo = 26
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        self.sound_speed = 34300
        
        # IR
        self.sensor_ir = 14
        GPIO.setup(self.sensor_ir,GPIO.IN)


    def esta_ponton(self):
        self.ponton = self.medir_si_esta_ponton()
        return self.ponton
        


    def ubicacion_cinta(self): # existen cuatro ubicaciones
        self.posicion_cinta_cm = self.medir_ubicacion_cinta()
        if 0 < self.posicion_cinta_cm < 15:
            self.posiciones_cinta = 0
        elif 16 < self.posicion_cinta_cm < 31:
            self.posiciones_cinta = 1
        elif  32 < self.posicion_cinta_cm < 47:
            self.posiciones_cinta = 2
        elif  48 < self.posicion_cinta_cm < 63:
            self.posiciones_cinta = 3
        else:
            print( "Fuera de rango")
            
        return self.posicion_cinta

    def medir_llenado_tachos(self):
        self.contenedores["1"] = medir_llenado()
        #self.contenedores[str(self.posicion_cinta)], self.contenedores[str(self.posicion_cinta + 4)] = medir_llenado()
        pass

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
            distancia = (sound_speed * duracion) / 20
            print( "Distancia: %.2f cm" % distancia)
            self.posicion_cinta = distancia
            return distancia
        
        
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
        self.direcction = 21
        self.step = 20
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
        
if __name__ == "__main__":
    # se setea con GPIO.BCM option means these are the numbers after "GPIO"
    #traslacion = Motores_traslacion()
    #time.sleep(1)
    #traslacion.start()
    #time.sleep(1)
    #print(threading.enumerate())
    #start_time = time.time()
    #finish_time = time.time()
    #time.sleep(2)
    #print("antes del while")
    #while finish_time - start_time < 8:
    #    traslacion.motores_status = "on"
    #    finish_time = time.time()
    #traslacion.motores_status = "off"
    #traslacion.clockwise = False
    #time.sleep(0.1)
    #start_time = time.time()
    #finish_time = time.time()
   
    #while finish_time - start_time < 8:
     #   traslacion.motores_status = "on"
     #   finish_time = time.time()

    #traslacion.motores_status = "off"    
    #traslacion.fin()
    
    
    ######## los 2 juntos
    traslacion = Motores_traslacion()
    maquina = Maquina_del_mal()
    time.sleep(1)
    traslacion.start()
    print("Arranca todo")
    print(threading.enumerate())
    maquina.medir_ubicacion_cinta()
    time.sleep(1)
    
    for x in range(1):            
        start_time = time.time()
        finish_time = time.time()
        print(x)
        while maquina.posicion_cinta < 20:
            traslacion.motores_status = "on"
            maquina.medir_ubicacion_cinta()
            finish_time = time.time()
        traslacion.motores_status = "off"
        maquina.medir_ubicacion_cinta()
        time.sleep(2)
    traslacion.fin()
    
